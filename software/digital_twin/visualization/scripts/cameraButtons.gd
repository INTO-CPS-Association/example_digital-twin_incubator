extends Node3D

@onready var camera_right = $CameraRight
@onready var camera_middle = $CameraMiddle
@onready var camera_left = $CameraLeft

func _on_left_button_pressed():
	camera_left.make_current()

func _on_middle_button_pressed():
	camera_middle.make_current()

func _on_right_button_pressed():
	camera_right.make_current()
