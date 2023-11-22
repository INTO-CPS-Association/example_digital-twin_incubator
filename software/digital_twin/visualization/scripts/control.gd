extends Node3D

signal heater_info(temp_val, is_on) 
signal fan_info(is_on) 
signal t1_sensor_info(val) 	# t1
signal t2_sensor_info(val) 	# t2
signal room_info(val) 		# t3 

func round_value(val): # two decimal
	return round(val * 100) / 100

func _on_message(message):
	var data = JSON.parse_string(message)
	
	print(data)
	if data.measurement == "low_level_driver":
		heater_info.emit(round_value(data.fields.average_temperature), 
						 data.fields.heater_on) 
		fan_info.emit(data.fields.fan_on)
		room_info.emit(data.fields.t3)
		
		t1_sensor_info.emit(round_value(data.fields.t1))
		t2_sensor_info.emit(round_value(data.fields.t2))
