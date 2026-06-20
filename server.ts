/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { initializeApp } from "firebase/app";
import { getFirestore, collection, addDoc, serverTimestamp, doc, getDoc, updateDoc } from "firebase/firestore";
import { parseWhatsAppMessage } from "./src/lib/gemini.js";
import fs from "fs";

const firebaseConfig = JSON.parse(fs.readFileSync("./firebase-applet-config.json", "utf8"));

// Initialize Firebase Client SDK (Server-side)
const app = initializeApp(firebaseConfig);
const db = getFirestore(app, firebaseConfig.firestoreDatabaseId);

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Routes
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok" });
  });

  // WhatsApp Webhook Mock
  app.post("/api/webhook/whatsapp", async (req, res) => {
    const { message, customer_phone } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }

    try {
      const parsedData = await parseWhatsAppMessage(message);
      const isAutoAck = parsedData.confidence >= 0.85;
      
      const orderData = {
        ...parsedData,
        customer_phone: customer_phone || "unknown",
        payment_status: 'pending',
        status: isAutoAck ? 'confirmed' : 'new',
        created_at: serverTimestamp(),
        updated_at: serverTimestamp(),
        raw_message: message
      };

      const orderRef = await addDoc(collection(db, "orders"), orderData);

      // Audit Record
      await addDoc(collection(db, "parser_audits"), {
        order_id: orderRef.id,
        raw_text: message,
        parsed_json: parsedData,
        confidence: parsedData.confidence,
        created_at: serverTimestamp()
      });

      // Generate Invoice if auto-confirmed
      if (isAutoAck) {
        const amount = (parsedData.items || []).length * 15; // Mock pricing RM15/item
        await addDoc(collection(db, "invoices"), {
          order_id: orderRef.id,
          customer_name: parsedData.customer_name || "Unknown",
          amount,
          payment_link: `https://duitnow.my/pay?to=ccam_mesh&amt=${amount}&ref=${orderRef.id}`,
          status: 'pending',
          created_at: serverTimestamp(),
          due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days due
        });
      }

      res.json({ id: orderRef.id, ...parsedData });
    } catch (error) {
      console.error("Webhook Error:", error);
      res.status(500).json({ error: "Internal Server Error" });
    }
  });

  // Update Order Status (Human-in-the-Loop Correction)
  app.patch("/api/orders/:id", async (req, res) => {
    const { id } = req.params;
    const updates = req.body;
    
    try {
      const orderRef = doc(db, "orders", id);
      const oldDoc = await getDoc(orderRef);
      
      await updateDoc(orderRef, {
        ...updates,
        updated_at: serverTimestamp()
      });

      // Special handling for confirmation (if it was just corrected)
      if (updates.status === 'confirmed' && oldDoc.data()?.status !== 'confirmed') {
        const order = oldDoc.data();
        const amount = (order?.items || []).length * 15;
        await addDoc(collection(db, "invoices"), {
          order_id: id,
          customer_name: updates.customer_name || order?.customer_name || "Unknown",
          amount,
          payment_link: `https://duitnow.my/pay?to=ccam_mesh&amt=${amount}&ref=${id}`,
          status: 'pending',
          created_at: serverTimestamp(),
          due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
        });
      }

      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  // Simulator Run Mock
  app.post("/api/simulate", async (req, res) => {
    const config = req.body;
    // Mock simulation logic reflecting business KPIs
    const results = {
      orders_processed: Math.floor(Math.random() * 500) + 100,
      parse_accuracy: 0.82 + Math.random() * 0.12,
      confidence_distribution: [
         { range: '0-20%', count: Math.floor(Math.random() * 10) },
         { range: '21-50%', count: Math.floor(Math.random() * 20) },
         { range: '51-80%', count: Math.floor(Math.random() * 50) + 30 },
         { range: '81-100%', count: Math.floor(Math.random() * 200) + 150 }
      ],
      avg_acknowledgement_time: (Math.random() * 8 + 2).toFixed(1), // seconds
      payment_conversion: (0.7 + Math.random() * 0.25).toFixed(2),
      admin_time_saved: Math.floor(Math.random() * 150) + 40, // man-minutes
      low_stock_events: Math.floor(Math.random() * 8),
      estimated_revenue: Math.floor(Math.random() * 12000) + 3000,
      duration_seconds: 60,
      timestamp: new Date().toISOString()
    };

    const simRef = await addDoc(collection(db, "simulations"), {
      config,
      results,
      created_at: serverTimestamp()
    });

    res.json({ id: simRef.id, results });
  });

  // Flows API
  app.get("/api/flows", async (req, res) => {
    try {
      const { getDocs } = await import("firebase/firestore");
      const snapshot = await getDocs(collection(db, "flows"));
      const flows = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      res.json(flows);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/flows", async (req, res) => {
    try {
      const flow = req.body;
      const docRef = await addDoc(collection(db, "flows"), {
        ...flow,
        created_at: serverTimestamp()
      });
      res.json({ id: docRef.id });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
