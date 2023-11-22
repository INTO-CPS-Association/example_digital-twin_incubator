extends Node3D

func _on_sensor_info(val):
	$T1TempLabel.text = str(val) + "°C"
