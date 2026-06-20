/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface OrderItem {
  name: string;
  qty: number;
  price?: number;
}

export interface Order {
  id?: string;
  customer_name: string;
  customer_phone: string;
  items: OrderItem[];
  delivery_address: string;
  pickup_time?: string;
  payment_method: string;
  payment_status: 'pending' | 'paid';
  status: 'new' | 'confirmed' | 'cooking' | 'ready' | 'delivered' | 'cancelled';
  confidence: number;
  raw_message: string;
  created_at: any;
  updated_at: any;
  corrected_at?: any;
  corrected_by?: string;
}

export interface Invoice {
  id?: string;
  order_id: string;
  customer_name: string;
  amount: number;
  payment_link: string;
  status: 'pending' | 'paid' | 'overdue';
  created_at: any;
  due_date: any;
}

export interface ParserAudit {
  id?: string;
  order_id: string;
  raw_text: string;
  parsed_json: any;
  confidence: number;
  corrected_by?: string;
  correction_timestamp?: any;
  created_at: any;
}

export interface InventoryItem {
  id?: string;
  name: string;
  stock_level: number;
  unit: string;
  low_stock_threshold: number;
}

export interface SimulationConfig {
  messages_per_minute: number;
  order_mix: string;
  error_rate: number;
  peak_hours: boolean;
}

export interface SimulationResult {
  id?: string;
  config: SimulationConfig;
  results: {
    orders_processed: number;
    parse_accuracy: number;
    low_stock_events: number;
    estimated_revenue: number;
    duration_seconds: number;
  };
  created_at: any;
}

export interface FlowDefinition {
  id?: string;
  name: string;
  definition: string;
  is_active: boolean;
}

export interface PilotMetrics {
  orders_processed: number;
  parse_accuracy: number;
  admin_time_saved_percent: number;
  payment_conversion_improvement: number;
  error_reduction_percent: number;
  nps_score: number;
  timestamp: any;
}

export interface Report {
  id?: string;
  type: 'weekly_snapshot' | 'roi_report' | 'simulation_summary';
  title: string;
  summary: string;
  metrics: Partial<PilotMetrics>;
  created_at: any;
  charts_data?: any;
}
