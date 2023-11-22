using Godot;
using System;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;
using System.Collections.Generic;

public partial class RBConnection : Node3D {
	private ConnectionFactory factory = new ConnectionFactory() {
		Uri = new Uri("amqp://incubator:incubator@localhost:5672")
	};
	private IConnection connection;
	private IModel channel;

	private string localQueue;
	private string exchangeName = "Incubator_AMQP";
	private string ROUTING_KEY_KF_PLANT_STATE = "incubator.record.kalmanfilter.plant.state";
	private string ROUTING_KEY_STATE = "incubator.record.driver.state";
	private List<string> messages = new();

	[Signal]
	public delegate void MessageEventHandler(string message);
	
	public override void _Ready() {
		connection = factory.CreateConnection();
		channel = connection.CreateModel();
		GD.Print("Connection created");

		localQueue = channel.QueueDeclare(autoDelete: true, exclusive: true);
		channel.QueueBind(queue: localQueue, exchange: exchangeName, routingKey: ROUTING_KEY_KF_PLANT_STATE);
		channel.QueueBind(queue: localQueue, exchange: exchangeName, routingKey: ROUTING_KEY_STATE);
		ReceiveMessage();
	}

	public override void _Process(double delta) {
		for (int i = 0; i < messages.Count; i++) {
			EmitSignal(SignalName.Message, messages[i]);
		}
		messages.Clear();
	}

	private void ReceiveMessage() {
		GD.Print("Waiting for messages");
		var consumer = new EventingBasicConsumer(channel);

		consumer.Received += (model, ea) => {
			var body = ea.Body.ToArray();
			var message = Encoding.ASCII.GetString(body);
			messages.Add(message);
		};

		channel.BasicConsume(queue: localQueue, autoAck: true, consumer: consumer);
	}
}
