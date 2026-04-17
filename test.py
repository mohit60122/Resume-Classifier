import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import warnings; warnings.filterwarnings('ignore')

from backend.ml.preprocessor import preprocess

df = pd.read_csv('backend/data/UpdatedResumeDataSet.csv')
for col in ['Resume_str', 'Resume', 'resume', 'Text', 'text']:
    if col in df.columns:
        text_col = col; break

df['cleaned'] = df[text_col].apply(lambda x: preprocess(str(x)))
df = df[df['cleaned'].str.len() > 10].reset_index(drop=True)

le = LabelEncoder()
y = le.fit_transform(df['Category'])

X = TfidfVectorizer(max_features=5000, sublinear_tf=True).fit_transform(df['cleaned'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"KNN Accuracy: {accuracy_score(y_test, KNeighborsClassifier(n_neighbors=5, metric='cosine').fit(X_train, y_train).predict(X_test)):.4f}")
print(f"Random Forest Accuracy: {accuracy_score(y_test, RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train, y_train).predict(X_test)):.4f}")
print(f"SVC Accuracy: {accuracy_score(y_test, SVC(kernel='linear', probability=True, random_state=42).fit(X_train, y_train).predict(X_test)):.4f}")
