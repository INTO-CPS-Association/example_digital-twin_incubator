# Experiment 

## Goal 

Calibration of plant models with an empty system. Closed lid.

## Author

Claudio Gomes

## Configuration

### Hardware

The current configuration as of the time of commit is used.

### Software 

The controller configuration was:
```
controller: {
    temperature_desired = 38.0,
    lower_bound = 2.0,
    heating_time = 60000.0, # Practically infinite
    heating_gap = 5.0
}
```

## Experiment Log and CSVs
- [20230501_calibration_empty_system.csv](20230501_calibration_empty_system.csv): the dataset.

Log (CEST):
- 2023-05-01 05:49:55 - Start experiment with empty lid for calibration
- 2023-05-01 07:35:34 - End Experiment with empty lid for calibration.

## Results and Discussion

Open the [interactive plot](./results.html)

![results.png](results.png)



