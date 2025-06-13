import sys
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QRadioButton, QGroupBox, QSpinBox, QScrollArea,
    QCheckBox, QSlider
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class ImageMerger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Merger")
        self.images = []
        self.current_merged = None
        self.preview_scale = 100  # %
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Buttons: file selection and settings
        btn_layout = QHBoxLayout()
        load_btn = QPushButton("Select Files")
        load_btn.clicked.connect(self.load_images)
        btn_layout.addWidget(load_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.toggle_settings)
        btn_layout.addWidget(settings_btn)

        main_layout.addLayout(btn_layout)

        # Settings panel (hidden by default)
        self.settings_box = QGroupBox("Merge Parameters")
        self.settings_box.setVisible(False)
        s_layout = QVBoxLayout()

        # Orientation
        orient_group = QGroupBox("Orientation")
        og_layout = QHBoxLayout()
        self.vert_radio = QRadioButton("Vertical")
        self.vert_radio.setChecked(True)
        self.horiz_radio = QRadioButton("Horizontal")
        og_layout.addWidget(self.vert_radio)
        og_layout.addWidget(self.horiz_radio)
        orient_group.setLayout(og_layout)
        s_layout.addWidget(orient_group)

        # Size (0 = auto)
        size_group = QGroupBox("Size (0 = auto)")
        sg_layout = QHBoxLayout()
        sg_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(0, 10000)
        sg_layout.addWidget(self.width_spin)
        sg_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, 10000)
        sg_layout.addWidget(self.height_spin)
        size_group.setLayout(sg_layout)
        s_layout.addWidget(size_group)

        # Padding between images
        pad_layout = QHBoxLayout()
        pad_layout.addWidget(QLabel("Padding:"))
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 1000)
        pad_layout.addWidget(self.padding_spin)
        s_layout.addLayout(pad_layout)

        # Centering
        self.centering_checkbox = QCheckBox("Center images")
        self.centering_checkbox.setChecked(True)
        s_layout.addWidget(self.centering_checkbox)

        self.settings_box.setLayout(s_layout)
        main_layout.addWidget(self.settings_box)

        # Preview scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Preview scale:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(400)
        self.scale_slider.setValue(100)
        self.scale_slider.setTickInterval(10)
        self.scale_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(self.scale_slider)
        self.scale_label = QLabel("100%")
        scale_layout.addWidget(self.scale_label)
        main_layout.addLayout(scale_layout)

        # Preview area
        self.preview_area = QScrollArea()
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(False)
        self.preview_area.setWidgetResizable(True)
        self.preview_area.setWidget(self.preview_label)
        main_layout.addWidget(self.preview_area, stretch=1)

        # Update/Save buttons
        action_layout = QHBoxLayout()
        merge_btn = QPushButton("Update Preview")
        merge_btn.clicked.connect(self.update_preview)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_image)
        action_layout.addWidget(merge_btn)
        action_layout.addWidget(save_btn)
        main_layout.addLayout(action_layout)

    def on_scale_changed(self, value):
        self.preview_scale = value
        self.scale_label.setText(f"{value}%")
        self.update_preview_pixmap()

    def load_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select images", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if files:
            self.images = files
            self.update_preview()

    def toggle_settings(self):
        self.settings_box.setVisible(not self.settings_box.isVisible())

    def update_preview(self):
        if not self.images:
            return

        # Load images with Pillow
        imgs = [Image.open(path) for path in self.images]

        # Resize if parameters set
        target_w = self.width_spin.value() or None
        target_h = self.height_spin.value() or None
        if target_w or target_h:
            resized = []
            for im in imgs:
                w, h = im.size
                new_w = target_w or int(w * (target_h / h))
                new_h = target_h or int(h * (target_w / w))
                resized.append(im.resize((new_w, new_h), Image.ANTIALIAS))
            imgs = resized

        padding = self.padding_spin.value()
        vertical = self.vert_radio.isChecked()
        centering = self.centering_checkbox.isChecked()

        # Calculate final canvas size
        if vertical:
            total_width = max(im.width for im in imgs)
            total_height = sum(im.height for im in imgs) + padding * (len(imgs) - 1)
        else:
            total_height = max(im.height for im in imgs)
            total_width = sum(im.width for im in imgs) + padding * (len(imgs) - 1)

        merged = Image.new("RGB", (total_width, total_height), (255, 255, 255))
        offset = 0
        for im in imgs:
            if vertical:
                x = (total_width - im.width) // 2 if centering else 0
                y = offset
            else:
                x = offset
                y = (total_height - im.height) // 2 if centering else 0
            merged.paste(im, (x, y))
            offset += (im.height if vertical else im.width) + padding

        self.current_merged = merged
        self.update_preview_pixmap()

    def update_preview_pixmap(self):
        if not self.current_merged:
            self.preview_label.clear()
            return
        pil_img = self.current_merged.convert("RGBA")
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)
        # Scale preview
        scale = self.preview_scale / 100.0
        if scale != 1.0:
            w = int(pix.width() * scale)
            h = int(pix.height() * scale)
            pix = pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(pix)
        self.preview_label.resize(pix.size())

    def save_image(self):
        if not self.current_merged:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save image", "", "PNG (*.png);;JPEG (*.jpg)"
        )
        if path:
            self.current_merged.save(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageMerger()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec_())
