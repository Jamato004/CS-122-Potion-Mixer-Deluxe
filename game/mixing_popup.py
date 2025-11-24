import pygame
from game.ui import Popup

# ---------------- Popup Handling ----------------
def handle_popup_event(scene, event):
    if event.type != pygame.MOUSEBUTTONDOWN or not hasattr(event, "pos"):
        return

    # Close
    if scene.popup.close_btn.is_clicked(event):
        scene.popup = None
        return

    # Mix
    if scene.popup.mix_btn.is_clicked(event):
        scene.mix_station(scene.popup.station_name)
        return

    # Slot clicks
    pos = event.pos
    for i, slot_rect in enumerate(scene.popup.slot_rects()):
        if not slot_rect.collidepoint(pos):
            continue
        station = scene.popup.station_name
        reqs = scene.station_slot_requirements.get(station, [])
        expected = reqs[i] if i < len(reqs) else None
        slots = scene.station_slots[station]

        if slots[i]:
            # remove from slot -> give back to inventory
            name = slots[i]
            cat = scene.ingredient_category.get(name, expected or "solid")
            scene.inventory.add_to_inventory(name, scene._kind_for(cat), 1)
            slots[i] = None
            scene.popup.slots = slots
            scene.layout_ingredient_buttons()
            scene.sfx_click.play()
            continue

        # place selected ingredient
        if not scene.selected_ingredient:
            scene.notification.set("Select an ingredient first", 1.4)
            scene.sfx_error.play()
            return

        sel_name = scene.selected_ingredient
        sel_cat = scene.ingredient_category.get(sel_name, None)
        if expected and expected != sel_cat:
            scene.notification.set(f"Needs {expected}", 1.4)
            scene.sfx_error.play()
            return

        kind = scene._kind_for(sel_cat or expected or "solid")
        if not scene.inventory.check_inventory(sel_name, kind):
            scene.notification.set("Out of stock", 1.2)
            scene.sfx_error.play()
            return

        # consume and place
        scene.inventory.remove_from_inventory(sel_name, kind, 1)
        slots[i] = sel_name
        scene.popup.slots = slots
        scene.selected_ingredient = None
        scene.layout_ingredient_buttons()
        scene.sfx_click.play()
        return

# ---------------- Popup Creation ----------------
def open_station_popup(scene, station_btn):
    name = station_btn.text
    w = 320
    slot_height = 38
    gap = 10
    top_margin = 40
    bottom_margin = 80

    slots = scene.station_slots.get(name, [])
    used_slots = len(slots)
    h = top_margin + used_slots * (slot_height + gap) + bottom_margin

    screen_w, screen_h = scene.screen.get_size()
    x = station_btn.rect.centerx - w // 2
    y = station_btn.rect.top - h - 8
    x = max(8, min(x, screen_w - w - 8))
    y = max(80, min(y, screen_h - h - 8))

    scene.popup = Popup(scene.screen, name, x, y, w, h, scene.small_font, used_slots)
    scene.popup.slots = slots.copy()
    reqs = scene.station_slot_requirements.get(name, [None] * used_slots)
    scene.popup.expected_types = reqs[:used_slots]

    print(f"Opened popup for {name} with {used_slots} slots")