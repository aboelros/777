"""
Telegram bot command handlers for AI Sales Commander.
Handles: /start, /products, /track, /rate
"""

from typing import Dict, Any, Optional
from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domains.products.models import Product
from app.domains.orders.models import Order
from app.domains.integrations.models import Integration
from app.core.database import AsyncSessionLocal

logger = structlog.get_logger(__name__)


async def handle_start_command(
    chat_id: str,
    project_id: UUID,
    telegram_service,
    db: AsyncSession
) -> None:
    """Handle /start command - show welcome and main menu."""
    welcome_message = """
🤖 <b>Welcome to AI Sales Commander!</b>

I'm your intelligent sales assistant. Here's what I can help you with:

<b>📦 /products</b> - Browse our product catalog
<b>📍 /track</b> - Track your orders
<b>⭐ /rate</b> - Rate your experience
<b>💬 Chat</b> - Ask me anything!

How can I assist you today?
"""
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📦 Products", "callback_data": "cmd_products"},
                {"text": "📍 Track Order", "callback_data": "cmd_track"}
            ],
            [
                {"text": "⭐ Rate Us", "callback_data": "cmd_rate"},
                {"text": "💬 Chat", "callback_data": "cmd_chat"}
            ]
        ]
    }
    
    await telegram_service.send_message(
        chat_id=chat_id,
        text=welcome_message,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    logger.info("Start command executed", chat_id=chat_id, project_id=str(project_id))


async def handle_products_command(
    chat_id: str,
    project_id: UUID,
    telegram_service,
    db: AsyncSession
) -> None:
    """Handle /products command - show product catalog."""
    try:
        # Fetch products for the project
        result = await db.execute(
            select(Product)
            .where(Product.project_id == project_id)
            .where(Product.is_active == True)
            .limit(5)
        )
        products = result.scalars().all()
        
        if not products:
            await telegram_service.send_message(
                chat_id=chat_id,
                text="📦 <b>No products available at the moment.</b>\n\nPlease check back later!",
                parse_mode="HTML"
            )
            return
        
        # Build product list message
        product_list = "📦 <b>Our Products:</b>\n\n"
        for i, product in enumerate(products, 1):
            price = f"${product.price}" if product.price else "Contact for price"
            stock = "✅ In Stock" if product.in_stock else "❌ Out of Stock"
            product_list += f"{i}. <b>{product.name}</b>\n"
            product_list += f"   💰 {price} | {stock}\n"
            if product.description:
                desc = product.description[:100] + "..." if len(product.description) > 100 else product.description
                product_list += f"   📝 {desc}\n"
            product_list += "\n"
        
        product_list += "\n💬 Reply with a product number to learn more or ask questions!"
        
        await telegram_service.send_message(
            chat_id=chat_id,
            text=product_list,
            parse_mode="HTML"
        )
        
        logger.info("Products command executed", chat_id=chat_id, product_count=len(products))
        
    except Exception as e:
        logger.error("Error handling products command", error=str(e))
        await telegram_service.send_message(
            chat_id=chat_id,
            text="❌ Error loading products. Please try again later."
        )


async def handle_track_command(
    chat_id: str,
    project_id: UUID,
    telegram_service,
    db: AsyncSession
) -> None:
    """Handle /track command - track orders."""
    try:
        # Fetch recent orders for the project
        result = await db.execute(
            select(Order)
            .where(Order.project_id == project_id)
            .order_by(Order.created_at.desc())
            .limit(5)
        )
        orders = result.scalars().all()
        
        if not orders:
            await telegram_service.send_message(
                chat_id=chat_id,
                text="📍 <b>No orders found.</b>\n\nYou haven't placed any orders yet. Browse our products to get started!",
                parse_mode="HTML"
            )
            return
        
        # Build order tracking message
        tracking_message = "📍 <b>Your Recent Orders:</b>\n\n"
        for i, order in enumerate(orders, 1):
            status_emoji = {
                "pending": "⏳",
                "processing": "⚙️",
                "shipped": "🚚",
                "delivered": "✅",
                "cancelled": "❌"
            }.get(order.status, "❓")
            
            tracking_message += f"{i}. {status_emoji} <b>Order #{order.id}</b>\n"
            tracking_message += f"   Status: {order.status.upper()}\n"
            tracking_message += f"   Total: ${order.total_amount if order.total_amount else 'N/A'}\n"
            if order.tracking_number:
                tracking_message += f"   🔗 Tracking: {order.tracking_number}\n"
            tracking_message += "\n"
        
        tracking_message += "\n💬 Reply with an order number for more details!"
        
        await telegram_service.send_message(
            chat_id=chat_id,
            text=tracking_message,
            parse_mode="HTML"
        )
        
        logger.info("Track command executed", chat_id=chat_id, order_count=len(orders))
        
    except Exception as e:
        logger.error("Error handling track command", error=str(e))
        await telegram_service.send_message(
            chat_id=chat_id,
            text="❌ Error loading orders. Please try again later."
        )


async def handle_rate_command(
    chat_id: str,
    project_id: UUID,
    telegram_service,
    db: AsyncSession
) -> None:
    """Handle /rate command - collect feedback."""
    rating_message = """
⭐ <b>We'd love your feedback!</b>

Please rate your experience with us:

1️⃣ - Poor
2️⃣ - Fair
3️⃣ - Good
4️⃣ - Very Good
5️⃣ - Excellent

Just reply with a number (1-5) and any comments!
"""
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "1️⃣", "callback_data": "rate_1"},
                {"text": "2️⃣", "callback_data": "rate_2"},
                {"text": "3️⃣", "callback_data": "rate_3"},
                {"text": "4️⃣", "callback_data": "rate_4"},
                {"text": "5️⃣", "callback_data": "rate_5"}
            ]
        ]
    }
    
    await telegram_service.send_message(
        chat_id=chat_id,
        text=rating_message,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    logger.info("Rate command executed", chat_id=chat_id, project_id=str(project_id))


async def process_telegram_command(
    text: str,
    chat_id: str,
    project_id: UUID,
    telegram_service,
    db: AsyncSession
) -> bool:
    """
    Process Telegram commands.
    Returns True if command was processed, False otherwise.
    """
    if not text:
        return False
    
    command = text.strip().lower()
    
    if command == "/start":
        await handle_start_command(chat_id, project_id, telegram_service, db)
        return True
    elif command == "/products":
        await handle_products_command(chat_id, project_id, telegram_service, db)
        return True
    elif command == "/track":
        await handle_track_command(chat_id, project_id, telegram_service, db)
        return True
    elif command == "/rate":
        await handle_rate_command(chat_id, project_id, telegram_service, db)
        return True
    
    return False
