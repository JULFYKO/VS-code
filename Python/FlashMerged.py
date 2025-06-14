import sys
import os
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QRadioButton, QGroupBox, QSpinBox, QScrollArea,
    QCheckBox, QSlider, QListWidget, QAbstractItemView, QMenu, QInputDialog, QMessageBox, QLineEdit
)
from PyQt5.QtGui import QPixmap, QImage, QColor, QPalette, QCursor, QPainter, QPen, QIcon
from PyQt5.QtCore import Qt, QPoint, QRect, QThread, pyqtSignal

# --- Async loader for images ---
class ImageLoaderThread(QThread):
    loaded = pyqtSignal(object, str)
    def __init__(self, path):
        super().__init__()
        self.path = path
    def run(self):
        try:
            img = Image.open(self.path).convert("RGBA")
            self.loaded.emit(img, self.path)
        except Exception:
            self.loaded.emit(None, self.path)

# --- Image item with meta ---
class ImageItem:
    def __init__(self, path, pil_image=None):
        self.path = path
        self.image = pil_image if pil_image is not None else None
        self.scale = 1.0
        self.offset = (0, 0)
        self.name = os.path.basename(path)
        self._cache = {}

    def get_scaled(self):
        if self.image is None:
            return None
        key = (self.scale, self.image.size)
        if key not in self._cache:
            w, h = self.image.size
            if self.scale == 1.0:
                self._cache[key] = self.image
            else:
                self._cache[key] = self.image.resize(
                    (int(w * self.scale), int(h * self.scale)),
                    Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
                )
        return self._cache[key]

    def clear_cache(self):
        self._cache.clear()

# --- Main Widget ---
class ImageMerger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Merger")
        self.setWindowIcon(QIcon.fromTheme("image-x-generic"))
        self.images = []
        self.current_merged = None
        self.preview_scale = 100
        self.dragging = False
        self.resizing = False
        self.drag_start = QPoint()
        self.selected_img_idx = None
        self.resize_handle_size = 12
        self._threads = []
        self.pending_loads = 0
        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        # --- Left: List and controls ---
        left = QVBoxLayout()
        # Search/filter
        search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search images...")
        self.search_box.textChanged.connect(self.filter_list)
        search_row.addWidget(self.search_box)
        left.addLayout(search_row)
        # Image list
        self.img_list = QListWidget()
        self.img_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.img_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.img_list.currentRowChanged.connect(self.on_img_selected)
        self.img_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.img_list.customContextMenuRequested.connect(self.show_list_menu)
        left.addWidget(self.img_list, 1)
        # Buttons
        btns = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.load_images)
        add_folder_btn = QPushButton("Folder")
        add_folder_btn.clicked.connect(self.load_folder)
        btns.addWidget(add_btn)
        btns.addWidget(add_folder_btn)
        left.addLayout(btns)
        order = QHBoxLayout()
        up_btn = QPushButton("↑")
        up_btn.clicked.connect(self.move_up)
        down_btn = QPushButton("↓")
        down_btn.clicked.connect(self.move_down)
        del_btn = QPushButton("Del")
        del_btn.clicked.connect(self.remove_selected)
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_selected)
        order.addWidget(up_btn)
        order.addWidget(down_btn)
        order.addWidget(del_btn)
        order.addWidget(rename_btn)
        left.addLayout(order)
        # Info
        self.info_label = QLabel("")
        left.addWidget(self.info_label)
        main_layout.addLayout(left, 1)

        # --- Right: Settings and preview ---
        right = QVBoxLayout()
        sbox = QGroupBox("Settings")
        s = QHBoxLayout()
        self.vert_radio = QRadioButton("Vertical")
        self.vert_radio.setChecked(True)
        self.horiz_radio = QRadioButton("Horizontal")
        s.addWidget(self.vert_radio)
        s.addWidget(self.horiz_radio)
        self.width_spin = QSpinBox(); self.width_spin.setRange(0, 10000)
        self.height_spin = QSpinBox(); self.height_spin.setRange(0, 10000)
        s.addWidget(QLabel("W:")); s.addWidget(self.width_spin)
        s.addWidget(QLabel("H:")); s.addWidget(self.height_spin)
        self.padding_spin = QSpinBox(); self.padding_spin.setRange(0, 1000)
        s.addWidget(QLabel("Pad:")); s.addWidget(self.padding_spin)
        self.centering_checkbox = QCheckBox("Center"); self.centering_checkbox.setChecked(True)
        s.addWidget(self.centering_checkbox)
        sbox.setLayout(s)
        right.addWidget(sbox)

        # Batch scale/offset
        batch_row = QHBoxLayout()
        batch_scale_btn = QPushButton("Batch Scale")
        batch_scale_btn.clicked.connect(self.batch_scale)
        batch_offset_btn = QPushButton("Batch Offset")
        batch_offset_btn.clicked.connect(self.batch_offset)
        batch_row.addWidget(batch_scale_btn)
        batch_row.addWidget(batch_offset_btn)
        right.addLayout(batch_row)

        # Preview scale
        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("Preview:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(400)
        self.scale_slider.setValue(100)
        self.scale_slider.setTickInterval(10)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        scale_row.addWidget(self.scale_slider)
        self.scale_label = QLabel("100%")
        scale_row.addWidget(self.scale_label)
        right.addLayout(scale_row)

        # Preview area
        self.preview_area = QScrollArea()
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(False)
        self.preview_area.setWidgetResizable(True)
        self.preview_area.setWidget(self.preview_label)
        right.addWidget(self.preview_area, 1)

        # Actions
        act = QHBoxLayout()
        merge_btn = QPushButton("Preview")
        merge_btn.clicked.connect(self.update_preview)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_image)
        export_btn = QPushButton("Export All")
        export_btn.clicked.connect(self.export_all)
        act.addWidget(merge_btn)
        act.addWidget(save_btn)
        act.addWidget(export_btn)
        right.addLayout(act)
        main_layout.addLayout(right, 3)

        self.preview_area.viewport().installEventFilter(self)
        self.preview_label.installEventFilter(self)
        self.preview_label.mousePressEvent = self.on_preview_mouse_press
        self.preview_label.mouseMoveEvent = self.on_preview_mouse_move
        self.preview_label.mouseReleaseEvent = self.on_preview_mouse_release

    def apply_dark_theme(self):
        dark = QPalette()
        dark.setColor(QPalette.Window, QColor(34, 34, 34))
        dark.setColor(QPalette.WindowText, Qt.white)
        dark.setColor(QPalette.Base, QColor(40, 40, 40))
        dark.setColor(QPalette.AlternateBase, QColor(34, 34, 34))
        dark.setColor(QPalette.ToolTipBase, Qt.white)
        dark.setColor(QPalette.ToolTipText, Qt.white)
        dark.setColor(QPalette.Text, Qt.white)
        dark.setColor(QPalette.Button, QColor(50, 50, 50))
        dark.setColor(QPalette.ButtonText, Qt.white)
        dark.setColor(QPalette.BrightText, Qt.red)
        dark.setColor(QPalette.Highlight, QColor(60, 120, 200))
        dark.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.instance().setPalette(dark)
        self.setStyleSheet("""
            QWidget { background: #222; color: #eee; }
            QGroupBox { border: 1px solid #444; margin-top: 8px; }
            QGroupBox:title { subcontrol-origin: margin; left: 8px; padding:0 2px 0 2px;}
            QPushButton { background: #333; color: #fff; border: 1px solid #444; padding: 4px 10px;}
            QPushButton:hover { background: #444; }
            QSlider::groove:horizontal { background: #333; height: 6px; border-radius: 3px;}
            QSlider::handle:horizontal { background: #666; border: 1px solid #888; width: 14px; margin: -4px 0; border-radius: 7px;}
            QListWidget { background: #232323; color: #fff; border: 1px solid #444;}
            QScrollArea { background: #232323; border: none;}
            QLabel { color: #eee; }
            QLineEdit { background: #232323; color: #fff; border: 1px solid #444; }
        """)

    # --- Image loading logic ---
    def load_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return
        self.pending_loads = len(files)
        self.img_list.setDisabled(True)
        self._threads = []
        for path in files:
            thread = ImageLoaderThread(path)
            thread.loaded.connect(self.on_image_loaded)
            thread.finished.connect(lambda t=thread: self._threads.remove(t) if t in self._threads else None)
            self._threads.append(thread)
            thread.start()

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if not folder:
            return
        exts = ('.png', '.jpg', '.jpeg', '.bmp')
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
        files.sort()
        if not files:
            return
        self.pending_loads = len(files)
        self.img_list.setDisabled(True)
        self._threads = []
        for path in files:
            thread = ImageLoaderThread(path)
            thread.loaded.connect(self.on_image_loaded)
            thread.finished.connect(lambda t=thread: self._threads.remove(t) if t in self._threads else None)
            self._threads.append(thread)
            thread.start()

    def on_image_loaded(self, pil_img, path):
        if pil_img is not None:
            item = ImageItem(path, pil_img)
            self.images.append(item)
            self.img_list.addItem(item.name)
        self.pending_loads -= 1
        if self.pending_loads == 0:
            self.img_list.setDisabled(False)
            if self.images:
                self.img_list.setCurrentRow(len(self.images)-1)
                self.update_preview()
            self.update_info()

    # --- List logic ---
    def filter_list(self, text):
        self.img_list.clear()
        for img in self.images:
            if text.lower() in img.name.lower():
                self.img_list.addItem(img.name)

    def refresh_list(self):
        sel = self.img_list.currentRow()
        self.img_list.clear()
        for img in self.images:
            self.img_list.addItem(img.name)
        if 0 <= sel < len(self.images):
            self.img_list.setCurrentRow(sel)

    def on_img_selected(self, idx):
        self.selected_img_idx = idx
        self.update_info()

    def show_list_menu(self, pos):
        idx = self.img_list.indexAt(pos).row()
        if idx < 0: return
        menu = QMenu()
        menu.addAction("Remove", lambda: self.remove_at(idx))
        menu.addAction("Rename", lambda: self.rename_at(idx))
        menu.addAction("Move Up", lambda: self.move_at(idx, -1))
        menu.addAction("Move Down", lambda: self.move_at(idx, 1))
        menu.addAction("Scale...", lambda: self.edit_scale(idx))
        menu.addAction("Offset...", lambda: self.edit_offset(idx))
        menu.exec_(QCursor.pos())

    def move_up(self):
        idx = self.img_list.currentRow()
        self.move_at(idx, -1)

    def move_down(self):
        idx = self.img_list.currentRow()
        self.move_at(idx, 1)

    def move_at(self, idx, delta):
        if 0 <= idx < len(self.images):
            new_idx = idx + delta
            if 0 <= new_idx < len(self.images):
                self.images[idx], self.images[new_idx] = self.images[new_idx], self.images[idx]
                self.refresh_list()
                self.img_list.setCurrentRow(new_idx)
                self.update_preview()

    def remove_selected(self):
        idx = self.img_list.currentRow()
        self.remove_at(idx)

    def remove_at(self, idx):
        if 0 <= idx < len(self.images):
            del self.images[idx]
            self.refresh_list()
            self.update_preview()
            self.update_info()

    def rename_selected(self):
        idx = self.img_list.currentRow()
        self.rename_at(idx)

    def rename_at(self, idx):
        if 0 <= idx < len(self.images):
            name, ok = QInputDialog.getText(self, "Rename", "New name:", text=self.images[idx].name)
            if ok and name:
                self.images[idx].name = name
                self.refresh_list()

    def edit_scale(self, idx):
        if 0 <= idx < len(self.images):
            val, ok = QInputDialog.getDouble(self, "Set scale", "Scale (1.0 = 100%)", self.images[idx].scale, 0.1, 10.0, 2)
            if ok:
                self.images[idx].scale = val
                self.images[idx].clear_cache()
                self.update_preview()

    def edit_offset(self, idx):
        if 0 <= idx < len(self.images):
            x, ok1 = QInputDialog.getInt(self, "Set offset X", "X offset (px)", self.images[idx].offset[0], -10000, 10000)
            if not ok1: return
            y, ok2 = QInputDialog.getInt(self, "Set offset Y", "Y offset (px)", self.images[idx].offset[1], -10000, 10000)
            if ok2:
                self.images[idx].offset = (x, y)
                self.update_preview()

    def batch_scale(self):
        val, ok = QInputDialog.getDouble(self, "Batch scale", "Set scale for all (1.0 = 100%)", 1.0, 0.1, 10.0, 2)
        if ok:
            for img in self.images:
                img.scale = val
                img.clear_cache()
            self.update_preview()

    def batch_offset(self):
        x, ok1 = QInputDialog.getInt(self, "Batch offset X", "X offset (px)", 0, -10000, 10000)
        if not ok1: return
        y, ok2 = QInputDialog.getInt(self, "Batch offset Y", "Y offset (px)", 0, -10000, 10000)
        if ok2:
            for img in self.images:
                img.offset = (x, y)
            self.update_preview()

    # --- Info ---
    def update_info(self):
        idx = self.img_list.currentRow()
        if 0 <= idx < len(self.images):
            img = self.images[idx]
            info = f"Name: {img.name} | Size: {img.image.size if img.image else '-'} | Scale: {img.scale:.2f} | Offset: {img.offset}"
        else:
            info = ""
        self.info_label.setText(info)

    # --- Preview logic ---
    def on_scale_changed(self, value):
        self.preview_scale = value
        self.scale_label.setText(f"{value}%")
        self.update_preview_pixmap()

    def update_preview(self):
        if not self.images:
            self.current_merged = None
            self.update_preview_pixmap()
            return
        imgs = []
        for imgitem in self.images:
            img = imgitem.get_scaled()
            if img is not None:
                imgs.append((img, imgitem.offset))
        target_w = self.width_spin.value() or None
        target_h = self.height_spin.value() or None
        padding = self.padding_spin.value()
        vertical = self.vert_radio.isChecked()
        centering = self.centering_checkbox.isChecked()
        if not imgs:
            self.current_merged = None
            self.update_preview_pixmap()
            return
        if vertical:
            total_width = max(im.width for im, _ in imgs)
            total_height = sum(im.height for im, _ in imgs) + padding * (len(imgs) - 1)
        else:
            total_height = max(im.height for im, _ in imgs)
            total_width = sum(im.width for im, _ in imgs) + padding * (len(imgs) - 1)
        if target_w: total_width = target_w
        if target_h: total_height = target_h
        merged = Image.new("RGBA", (total_width, total_height), "#222")
        offset = 0
        for im, (ox, oy) in imgs:
            if vertical:
                x = (total_width - im.width) // 2 if centering else 0
                x += ox
                y = offset + oy
            else:
                x = offset + ox
                y = (total_height - im.height) // 2 if centering else 0
                y += oy
            merged.alpha_composite(im, (x, y))
            offset += (im.height if vertical else im.width) + padding
        self.current_merged = merged
        self.update_preview_pixmap()

    def update_preview_pixmap(self):
        if not self.current_merged:
            self.preview_label.clear()
            return
        pil_img = self.current_merged
        scale = self.preview_scale / 100.0
        w, h = pil_img.width, pil_img.height
        preview_img = pil_img.copy()
        if scale != 1.0 or max(w, h) > 2000:
            preview_img.thumbnail((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS)
        data = preview_img.convert("RGBA").tobytes("raw", "RGBA")
        qimg = QImage(data, preview_img.width, preview_img.height, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)
        # Draw selection rectangle if image selected
        if self.selected_img_idx is not None and 0 <= self.selected_img_idx < len(self.images):
            painter = QPainter(pix)
            im = self.images[self.selected_img_idx].get_scaled()
            ox, oy = self.images[self.selected_img_idx].offset
            vertical = self.vert_radio.isChecked()
            centering = self.centering_checkbox.isChecked()
            offset = 0
            for idx, img in enumerate(self.images):
                if idx == self.selected_img_idx:
                    if im is None: break
                    if vertical:
                        x = (pix.width() - im.width * scale) // 2 if centering else 0
                        x += ox * scale
                        y = offset * scale + oy * scale
                    else:
                        x = offset * scale + ox * scale
                        y = (pix.height() - im.height * scale) // 2 if centering else 0
                        y += oy * scale
                    rect = QRect(int(x), int(y), int(im.width * scale), int(im.height * scale))
                    pen = QPen(QColor("#44aaff"), 2, Qt.DashLine)
                    painter.setPen(pen)
                    painter.drawRect(rect)
                    handle = QRect(rect.right()-self.resize_handle_size, rect.bottom()-self.resize_handle_size,
                                   self.resize_handle_size, self.resize_handle_size)
                    painter.fillRect(handle, QColor("#44aaff"))
                    break
                offset += (img.get_scaled().height if vertical else img.get_scaled().width) + self.padding_spin.value()
            painter.end()
        self.preview_label.setPixmap(pix)
        self.preview_label.resize(pix.size())

    def save_image(self):
        if not self.current_merged:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save image", "", "PNG (*.png);;JPEG (*.jpg)")
        if path:
            self.current_merged.save(path)

    def export_all(self):
        if not self.images:
            return
        folder = QFileDialog.getExistingDirectory(self, "Export all images to folder")
        if not folder:
            return
        for img in self.images:
            if img.image:
                out_path = os.path.join(folder, img.name)
                img.image.save(out_path)
        QMessageBox.information(self, "Export", "All images exported.")

    def eventFilter(self, obj, event):
        if obj in (self.preview_area.viewport(), self.preview_label):
            if event.type() == event.Wheel:
                delta = event.angleDelta().y()
                if delta > 0:
                    self.preview_scale = min(400, self.preview_scale + 10)
                else:
                    self.preview_scale = max(10, self.preview_scale - 10)
                self.scale_slider.setValue(self.preview_scale)
                self.scale_label.setText(f"{self.preview_scale}%")
                self.update_preview_pixmap()
                return True
        return super().eventFilter(obj, event)

    def on_preview_mouse_press(self, event):
        if event.button() == Qt.LeftButton and self.selected_img_idx is not None and 0 <= self.selected_img_idx < len(self.images):
            im = self.images[self.selected_img_idx].get_scaled()
            scale = self.preview_scale / 100.0
            vertical = self.vert_radio.isChecked()
            centering = self.centering_checkbox.isChecked()
            offset = 0
            found = False
            for idx, img in enumerate(self.images):
                if idx == self.selected_img_idx:
                    ox, oy = img.offset
                    if im is None: break
                    if vertical:
                        x = (self.preview_label.width() - im.width * scale) // 2 if centering else 0
                        x += ox * scale
                        y = offset * scale + oy * scale
                    else:
                        x = offset * scale + ox * scale
                        y = (self.preview_label.height() - im.height * scale) // 2 if centering else 0
                        y += oy * scale
                    rect = QRect(int(x), int(y), int(im.width * scale), int(im.height * scale))
                    handle = QRect(rect.right()-self.resize_handle_size, rect.bottom()-self.resize_handle_size,
                                   self.resize_handle_size, self.resize_handle_size)
                    if handle.contains(event.pos()):
                        self.resizing = True
                        self.resize_start = event.pos()
                        self.orig_scale = img.scale
                        found = True
                        break
                    elif rect.contains(event.pos()):
                        self.dragging = True
                        self.drag_start = event.pos()
                        self.orig_offset = img.offset
                        found = True
                        break
                offset += (img.get_scaled().height if vertical else img.get_scaled().width) + self.padding_spin.value()
            if not found:
                self.dragging = False
                self.resizing = False

    def on_preview_mouse_move(self, event):
        if self.resizing and self.selected_img_idx is not None and 0 <= self.selected_img_idx < len(self.images):
            img = self.images[self.selected_img_idx]
            im = img.get_scaled()
            scale = self.preview_scale / 100.0
            dx = event.pos().x() - self.resize_start.x()
            new_scale = max(0.1, self.orig_scale + dx / (im.width * scale if im else 1))
            img.scale = new_scale
            img.clear_cache()
            self.update_preview()
        elif self.dragging and self.selected_img_idx is not None and 0 <= self.selected_img_idx < len(self.images):
            dx = int((event.pos().x() - self.drag_start.x()) / (self.preview_scale / 100.0))
            dy = int((event.pos().y() - self.drag_start.y()) / (self.preview_scale / 100.0))
            ox, oy = self.orig_offset
            self.images[self.selected_img_idx].offset = (ox + dx, oy + dy)
            self.update_preview()

    def on_preview_mouse_release(self, event):
        self.dragging = False
        self.resizing = False

    def closeEvent(self, event):
        for t in list(self._threads):
            t.quit()
            t.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageMerger()
    window.resize(1100, 700)
    window.show()
    sys.exit(app.exec_())
