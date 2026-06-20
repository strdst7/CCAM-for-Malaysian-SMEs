import { initializeApp } from "firebase/app";
import { getFirestore, collection, addDoc, serverTimestamp } from "firebase/firestore";
import fs from "fs";

const firebaseConfig = JSON.parse(fs.readFileSync("./firebase-applet-config.json", "utf8"));

const app = initializeApp(firebaseConfig);
const db = getFirestore(app, firebaseConfig.firestoreDatabaseId);

const orders = [
  {
    customer_name: "Siti Nurhaliza",
    customer_phone: "+60123456789",
    items: [{ name: "Nasi Lemak Ayam", qty: 2 }, { name: "Teh Tarik", qty: 2 }],
    delivery_address: "Jalan Ampang 12, KL",
    status: "confirmed",
    confidence: 0.98,
    raw_message: "Hi, I want 2 nasi lemak ayam and 2 teh tarik to Jalan Ampang 12. Thanks Siti.",
    created_at: serverTimestamp()
  },
  {
    customer_name: "Ah Keong",
    customer_phone: "+60198765432",
    items: [{ name: "Char Kway Teow", qty: 1 }],
    delivery_address: "Petaling Jaya Sec 14",
    status: "new",
    confidence: 0.72,
    raw_message: "Char kway teow 1, send to PJ sec 14. How much?",
    created_at: serverTimestamp()
  }
];

const flows = [
  {
    name: "Standard F&B Takeaway",
    definition: "trigger: message_received\nactions:\n  - type: parser\n    engine: gemini_flash_low_latency\n    confidence_threshold: 0.85\n  - type: logic\n    condition: stock_available\n    true:\n      - create_invoice\n      - send_whatsapp_ack",
    created_at: serverTimestamp()
  }
];

async function seed() {
  console.log("Seeding data with Client SDK...");
  try {
    for (const order of orders) {
      await addDoc(collection(db, "orders"), order);
      console.log(`Added order for ${order.customer_name}`);
    }
    for (const flow of flows) {
      await addDoc(collection(db, "flows"), flow);
      console.log(`Added flow: ${flow.name}`);
    }
    console.log("Seed complete!");
  } catch (err) {
    console.error("Seed failed:", err);
  }
}

seed();
