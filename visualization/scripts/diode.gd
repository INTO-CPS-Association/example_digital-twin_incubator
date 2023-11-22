extends Node3D

var material : StandardMaterial3D 

func _ready():
	material = $Color.get("surface_material_override/0")

func _on_fan_info(is_on):
	if is_on:
		material.albedo_color = Color.GREEN
	else:
		material.albedo_color = Color.RED
