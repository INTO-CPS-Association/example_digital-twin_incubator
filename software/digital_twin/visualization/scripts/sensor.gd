extends Node3D

func _on_sensor_info(t1, t2):
	$T1TempLabel.text = str(t1) + "°C"
	$T2TempLabel.text = str(t2) + "°C"
