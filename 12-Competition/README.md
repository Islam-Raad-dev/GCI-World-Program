# In-class Competition: Home Credit Default Risk
## GCI Global 2026
### Competition Starts: October 2nd
### Competition Ends: November 20th 1:00AM UTC
### Ranking Announcement: December 17th (Session 14)

---

## About the Assignment
---

In this competition, you will work on the **“Home Credit Default Risk”** competition, which was originally held on Kaggle in 2018 [[1](https://www.kaggle.com/c/home-credit-default-risk/overview/description)]. While the original competition provided multiple datasets, this competition will use only a subset of them.

The goal of this competition is to **predict whether a given data entry (representing a customer) is likely to default (= fail to make a required payment) on their loan based on a variety of customer data provided**. Your task is to create a machine learning model that best predicts the **probability of default for each customer**.

---

## How to Get Started
---

### Data
Once you unzip the `competition.zip` file, you should see the following files inside `competition` folder:
* `README.ipynb`: This notebook
* `tutorial.ipynb`: Tutorial notebook to get started on the competition
* `HomeCredit_columns_description.xlsx`: Descriptions about the dataset
* `input` folder
    * `train.csv`: Data to **train** your own machine learning model
        * `TARGET` column is the target variable
            * `1` indicates payment difficulties (default)
            * `0` indicates no payment difficulties
        * All other columns are explanatory variables
    * `test.csv`: Data to **evaluate** your trained model. You will be competing to achieve higher prediction accuracy on this data.
    * `sample_submission.csv`: Example of the CSV file to submit

### First Steps
Open the `tutorial.ipynb` and run all cells. This will create a new file, `output/submission.csv`. Download the file to your PC, then upload on Omnicampus. You should then be able to see your score on the leaderboard.

### How to Improve Your Model
Here are some tips to get a higher ranking on the competition:
- [ ] **Step 1: Understand the data using visualizations**
- [ ] **Step 2: Preprocess the data**
    - Decide what preprocessing is needed based on your findings from Step 1
    - The tutorial only uses 5 features to create the model, so try adding more features
- [ ] **Step 3: Improve your model**
    - Optimize the hyperparameters of your model
    - Explore different models

We will also share some techniques you can use in lectures and office hours, so stay tuned!

---

## Evaluation
---

### Evaluation Metric

The competition will be judged based on the [Area Under the Curve (AUC) of the ROC curve](https://en.wikipedia.org/wiki/Receiver_operating_characteristic) between the predicted probabilities and the ground truth for the test data.

### Submission
Predictions must be submitted via the **Omnicampus** platform. The format of the submitted data should be a CSV file as shown below.

| SK_ID_CURR | TARGET |
| :--- | :--- |
| 171202 | 0.5 |
| 171203 | 0.5 |
| 171204 | 0.5 |
| … | … |
| 232699 | 0.5 |
| 232700 | 0.5 |
| 232701 | 0.5 |

Please follow the format shown in **sample_submission.csv**. Submissions not adhering to this format will receive a score of -1, so please check your file format if you encounter this issue.

### Scoring
During the competition period, scoring will be conducted on a subset of the test data to prevent "leaderboard overfitting". The leaderboard on Omnicampus will display your scores based on these interim results. This leaderboard is referred to as the **Public Leaderboard**.

After the competition ends, final scoring will be performed on the entire test data. The final rankings will be determined based on this comprehensive evaluation. The leaderboard generated from this final scoring is referred to as the **Private Leaderboard**.

**Note:**
- You can submit as many times as you want. However, the final rankings will be determined based on your **last submitted file**.
- It may take **several minutes to score your submission**. Please make sure to check if the scoring timestamp has been updated. If not, please wait patiently and try reloading the page.
- **If you wish to be considered for Honors or Outstanding Student, you are required to submit code that can reproduce the CSV file you submitted.**

---

## Rules 🚨
---

- **Prohibition of External Data Usage**  
  No external data may be used at any stage of the analysis. You must rely solely on the provided datasets (`input/train.csv` and `input/test.csv`).

- **Prohibition of Hand-Labeling**  
  Creating predictions manually instead of using a model is referred to as Hand-Labeling, and it is prohibited in most data science competitions. This rule also applies to this competition, prohibiting Hand-Labeling for all or part of the test data. **Making manual decisions for part of the predictions** based on rules or specific conditions derived from EDA (Exploratory Data Analysis) also falls under Hand-Labeling. All predictions must be generated by a model, and manual predictions are not permitted. Data processing must be based on reproducible methods, and the submitted predictions must be **automatically generated** by a model that can also be applied to other data with similar characteristics.

- **Ensuring Reproducibility**  
  Ensure reproducibility of your predictions as much as possible. To achieve this, it is essential to **set seed values for random number generation**.

  The phrase "as much as possible" is used because there are situations where reproducibility cannot be fully guaranteed. For example, recent updates to the PyTorch deep learning framework have caused overall precision to decrease. In such cases, reproducing predictions made with an earlier version would require downgrading the framework. However, for this competition, such measures are not required to ensure reproducibility.

- **Permission for Private Sharing**  
  In data science competitions, private information sharing is typically strictly regulated from a fairness perspective. In most cases, information sharing within a team is only permitted when the team formation is declared through official channels. Personal information sharing outside the team, referred to as **Private Sharing**, is strictly prohibited.

  However, since this competition is positioned as a tutorial for beginners, the Private Sharing prohibition will not be applied. If you have experienced individuals nearby, you are encouraged to actively seek their advice, and you may also exchange information and discuss with other participants online. When engaging in online discussions with other participants, please try to conduct these interactions in public forums rather than private channels, ensuring that all participants can share insights.

- **Citing Original Sources (Reference Code)**  
  This competition has numerous high-quality and informative notebooks reported on the internet. Exploring such excellent approaches and deciphering code is also a form of learning, so please feel free to reference them. There is absolutely no problem with referencing others' code.

  From an educational standpoint, GCI distinguishes between one's own work and citations. Therefore, when you quote code, please explicitly indicate the original source. For top-ranking participants in this competition, code disclosure is required. If it is discovered during this disclosure that the original source was not cited, and the code is clearly from another source, there is a possibility that the prize may be revoked. Therefore, it is recommended to keep a record of the notebooks you referenced to track which codes you have used.