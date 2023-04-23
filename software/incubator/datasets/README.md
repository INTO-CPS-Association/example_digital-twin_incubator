# Datasets

This folder contains all datasets from real experiments with the incubator.

Requirements for a good dataset:
1. Must be contained in a folder, whose name must include the day that the experiment was started, followed by the goal of the experiment. See existing datasets for inspiration.
2. Must contain a README.md file, documenting at least the following:
   1. The goal of the experiment.
   2. Who run the experiment.
   2. A summary of the configuration (just enough for the reader to be able to assess whether the dataset corresponds to the most recent hardware configuration).
      1. Hardware
      2. Controller parameters (if relevant)
   3. An experiment log, with optional pictures.
   4. There should be a test that loads and displays a relevant portion of the data.
   5. A discussion of the results obtained, containing plots and all that.
3. Must contain one or more csv file containing the full dataset. If more than one csv, then the README file most describe what each file means. 
