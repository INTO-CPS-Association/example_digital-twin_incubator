using Godot;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System;
using System.Collections.Generic;
using System.Text;

public partial class Global : Node
{
    private ConnectionFactory factory = new ConnectionFactory();
    private IConnection connection;
	private IModel channel;

    private string exchangeName = "Incubator_AMQP";
    private string ROUTING_KEY_KF_PLANT_STATE = "incubator.record.kalmanfilter.plant.state";
    private string ROUTING_KEY_STATE = "incubator.record.driver.state";
    private string localQueue;
	private List<string> messages = new();

    public LineEdit userName;
    public LineEdit hostName;
    public LineEdit password;
    public LineEdit port;

    [Signal]
    public delegate void OnMessageEventHandler(string message);

    public bool ConnectToRabbitMQ()
    {
        if (userName.Text != "") {
            factory.UserName = userName.Text;
            GD.Print("Host name set to: " + userName.Text);
        }

        if (hostName.Text != "") {
            GD.Print("Host name set to: " + hostName.Text);
        } 

        if (password.Text != "") {
            factory.Password = password.Text;
            GD.Print("Password set to: " + password.Text);
        } 

        if (port.Text != "") {
            factory.Port = port.Text.ToInt();
        } 
        else {
            factory.Port = 5672;
            GD.Print("Port not set, using default: 5672");
        }

        connection = factory.CreateConnection();
        channel = connection.CreateModel();
        
        localQueue = channel.QueueDeclare(autoDelete: true, exclusive: true); 
        channel.QueueBind(queue: localQueue, exchange: exchangeName, routingKey: ROUTING_KEY_KF_PLANT_STATE);
        channel.QueueBind(queue: localQueue, exchange: exchangeName, routingKey: ROUTING_KEY_STATE);
        ReceiveMessage();
        
        if (!connection.IsOpen) {
            return false;
        }

        return true;
    }

	public override void _Process(double delta) {
		for (int i = 0; i < messages.Count; i++) {
			EmitSignal(SignalName.OnMessage, messages[i]);
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