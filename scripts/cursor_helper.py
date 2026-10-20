import math
import time

CURSOR_INJECTION_JS = """
(() => {
    if (document.getElementById('virtual-cursor-pointer')) return;

    const cursor = document.createElement('div');
    cursor.id = 'virtual-cursor-pointer';
    cursor.style.position = 'fixed';
    cursor.style.top = '0px';
    cursor.style.left = '0px';
    cursor.style.width = '24px';
    cursor.style.height = '24px';
    cursor.style.pointerEvents = 'none';
    cursor.style.zIndex = '99999999';
    cursor.style.transition = 'transform 0.04s linear';
    cursor.style.filter = 'drop-shadow(0 2px 6px rgba(0,0,0,0.75))';
    cursor.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 2L18 13L11.5 14L8 21L4 2Z" fill="#38bdf8" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>
        </svg>
    `;
    document.documentElement.appendChild(cursor);

    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes rippleAnim {
            0% { transform: scale(0.2); opacity: 1; }
            100% { transform: scale(2.4); opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    window.addEventListener('mousemove', (e) => {
        cursor.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
    });

    window.addEventListener('mousedown', (e) => {
        const ripple = document.createElement('div');
        ripple.style.position = 'fixed';
        ripple.style.left = `${e.clientX - 16}px`;
        ripple.style.top = `${e.clientY - 16}px`;
        ripple.style.width = '32px';
        ripple.style.height = '32px';
        ripple.style.borderRadius = '50%';
        ripple.style.backgroundColor = 'rgba(56, 189, 248, 0.4)';
        ripple.style.border = '2px solid rgba(255, 255, 255, 0.95)';
        ripple.style.pointerEvents = 'none';
        ripple.style.zIndex = '99999998';
        ripple.style.animation = 'rippleAnim 0.45s ease-out forwards';
        document.documentElement.appendChild(ripple);
        setTimeout(() => ripple.remove(), 450);
    });
})();
"""

current_mouse_pos = {"x": 500, "y": 300}

def inject_cursor(page):
    page.add_init_script(CURSOR_INJECTION_JS)
    page.evaluate(CURSOR_INJECTION_JS)

def smooth_move(page, target_x, target_y, steps=20, sleep_per_step=0.015):
    global current_mouse_pos
    start_x = current_mouse_pos["x"]
    start_y = current_mouse_pos["y"]
    
    for i in range(1, steps + 1):
        t = i / steps
        # smooth ease-in-out curve
        ease = 0.5 - 0.5 * math.cos(t * math.pi)
        x = start_x + (target_x - start_x) * ease
        y = start_y + (target_y - start_y) * ease
        page.mouse.move(x, y)
        time.sleep(sleep_per_step)
        
    current_mouse_pos["x"] = target_x
    current_mouse_pos["y"] = target_y

def move_and_click(page, locator, steps=25):
    try:
        box = locator.bounding_box()
        if box:
            target_x = box["x"] + box["width"] / 2
            target_y = box["y"] + box["height"] / 2
            smooth_move(page, target_x, target_y, steps=steps)
            time.sleep(0.1)
            page.mouse.down()
            time.sleep(0.12)
            page.mouse.up()
            time.sleep(0.15)
        else:
            locator.click()
    except Exception:
        locator.click()
