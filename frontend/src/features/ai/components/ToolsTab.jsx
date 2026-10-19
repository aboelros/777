import React from 'react';
import { motion } from 'framer-motion';
import { Wrench, CheckCircle2, ShoppingBag, Search, Truck, Clock, Headphones, Calculator } from 'lucide-react';

const AI_TOOLS = [
  {
    id: 'check_inventory',
    name: 'فحص المخزون والأسعار (check_inventory)',
    icon: Search,
    category: 'Sales & Catalog',
    desc: 'البحث المباشر في كتالوج المنتجات، التأكد من توافر المقاسات والألوان، وجلب الأسعار الحقيقية فوراً.',
    params: 'query (اسم المنتج أو الفئة أو "all" للكتالوج كامل)',
    status: 'Active',
  },
  {
    id: 'create_order',
    name: 'إنشاء وتأكيد الطلب (create_order)',
    icon: ShoppingBag,
    category: 'Orders & Checkout',
    desc: 'إنشاء أوردر مبيعات رسمي مباشرة من المحادثة بعد جمع بيانات العميل (الاسم، الهاتف، العنوان، المنتجات).',
    params: 'customer_name, customer_phone, delivery_address, items',
    status: 'Active',
  },
  {
    id: 'track_order',
    name: 'تتبع الشحنات والطلبات (track_order)',
    icon: Truck,
    category: 'Fulfillment & Logistics',
    desc: 'معرفة حالة الطلب وموعد التوصيل للعميل بمجرد إدخال رقم الطلب أو رقم هاتف العميل.',
    params: 'order_id أو phone_number',
    status: 'Active',
  },
  {
    id: 'fetch_order_details',
    name: 'مراجعة تفاصيل الطلب (fetch_order_details)',
    icon: ShoppingBag,
    category: 'Orders',
    desc: 'استعراض الأصناف المحجوزة وقيمة الطلب السابقة للعميل للرد على أي تعديل أو استفسار.',
    params: 'order_id',
    status: 'Active',
  },
  {
    id: 'calculate_shipping_and_tax',
    name: 'حساب مصاريف الشحن (calculate_shipping_and_tax)',
    icon: Calculator,
    category: 'Pricing',
    desc: 'احتساب تكلفة التوصيل الدقيقة بناءً على المحافظة أو المدينة وإضافتها لإجمالي الفاتورة.',
    params: 'city, country, cart_total',
    status: 'Active',
  },
  {
    id: 'schedule_followup',
    name: 'المتابعة الذكية بعد الشراء (schedule_followup)',
    icon: Clock,
    category: 'Retention',
    desc: 'جدولة رسالة اطمئنان ودية للعميل بعد 24 ساعة من التوصيل وطلب تقييم بعد 3 أيام لزيادة الرضا.',
    params: 'customer_id, delay_hours, followup_reason',
    status: 'Active',
  },
  {
    id: 'create_support_ticket',
    name: 'تحويل للدعم البشري (create_support_ticket)',
    icon: Headphones,
    category: 'Support Escalation',
    desc: 'إنشاء تذكرة دعم وإشعار فريق العمل فوراً عند وجود طلب خاص أو استفسار يحتاج تدخل يدوي.',
    params: 'subject, priority, customer_issue',
    status: 'Active',
  },
];

export default function ToolsTab() {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Wrench className="w-5 h-5 text-accent-primary" />
              أدوات وقدرات البوت المفعلة (AI Tools & Functions)
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              هذه الأدوات يستدعيها البوت تلقائياً أثناء الدردشة لتنفيذ عمليات حقيقية كفحص المخزن وإنشاء الأوردرات.
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold w-fit">
            <CheckCircle2 className="w-4 h-4" />
            7 أدوات متصلة وجاهزة للعمل
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {AI_TOOLS.map((tool) => {
            const Icon = tool.icon;
            return (
              <div
                key={tool.id}
                className="p-5 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-xl bg-accent-primary/10 text-accent-primary">
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-bold text-white text-sm">{tool.name}</h3>
                        <span className="text-[11px] text-gray-400">{tool.category}</span>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400">
                      مفعل
                    </span>
                  </div>
                  <p className="text-xs text-gray-300 leading-relaxed mb-4">{tool.desc}</p>
                </div>

                <div className="pt-3 border-t border-white/5 text-[11px] text-gray-400 flex items-center gap-1 font-mono">
                  <span className="text-gray-500 font-bold">المدخلات:</span>
                  <span className="truncate text-gray-300">{tool.params}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
