extends Node3D

func _on_sensor_info(val):
	$T2TempLabel.text = str(val) + "°C"
