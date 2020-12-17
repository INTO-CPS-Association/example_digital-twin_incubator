# Digit Lunch Presentation Feedback

Video: https://web.microsoftstream.com/video/d2528dd5-eac5-47d5-beb2-19a9b5966a4b

# Giuseppe

We should use a filter that works with co-simulations, like a Bayesian Kalman filter.

# Emil

We also need a noise model for the kalman filter.

# Christian

I think the incubator has clear real world counterparts, like an actual incubator for biological tests, heating of a building, etc, it should be straight forward to make a link
Here its also easy to make a case for visualization, suppose that a building has 100 temperature sensors


## Terms:

	* Digital Shadow -> implies passive, following entity. Has negative connotation too, it is "bad" and it "obscures/overshadows" things
	
## Kalman Filter:
	* Does it not require that the system dynamics can be described using a matrix, A?
	* Piecewise linearization?
	* How do i know that kalman filters will work for "complex" systems.

## Slides
	* 12: add time series plot and link the trajectories to the quantities
	* 17: Maybe plot risidual?	
	* 12 : I only need to determine the ideal control parameters once, why do i need the full digital twin?

## Case study:

	* Link this with "real word application", incubate bacteria in petri dishes?
	* How would digital twins benefit this setup?
	
## Visualization:
	
	Dashboards:
	* DL -> Tensorboard 
	* IoT -> 
	* 

## What-If Simulations:

	* 20. Why do i need digital shadow or twin for doing this?

## Fault tolerance:

	* 23. Why do i not implement the kalman filter in the controller? Where does the twin add value? -> More computing power, higher flexibility
	
