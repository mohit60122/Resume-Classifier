import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.multiclass import OneVsRestClassifier
import warnings
warnings.filterwarnings('ignore')
import re

df = pd.read_csv('backend/data/UpdatedResumeDataSet.csv')
text_col = 'Category' # fallback
for col in ['Resume_str', 'Resume', 'resume', 'Text', 'text']:
    if col in df.columns:
        text_col = col; break

def cleanResume(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText)
    resumeText = re.sub('RT|cc', ' ', resumeText)
    resumeText = re.sub('#\S+', '', resumeText)
    resumeText = re.sub('@\S+', '  ', resumeText)
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', resumeText)
    resumeText = re.sub(r'[^\x00-\x7f]', r' ', resumeText) 
    resumeText = re.sub('\s+', ' ', resumeText)
    return resumeText

df['cleaned'] = df[text_col].apply(lambda x: cleanResume(str(x)))

le = LabelEncoder()
y = le.fit_transform(df['Category'])

# Standard configuration
tfidf = TfidfVectorizer(max_features=1500, stop_words='english', sublinear_tf=True)
X = tfidf.fit_transform(df['cleaned']).toarray()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f'Kaggle KNeighborsClassifier: {accuracy_score(y_test, OneVsRestClassifier(KNeighborsClassifier()).fit(X_train, y_train).predict(X_test)):.4f}')
print(f'LinearSVC: {accuracy_score(y_test, LinearSVC(random_state=42).fit(X_train, y_train).predict(X_test)):.4f}')
print(f'RandomForest: {accuracy_score(y_test, RandomForestClassifier(random_state=42).fit(X_train, y_train).predict(X_test)):.4f}')
