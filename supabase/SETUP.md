# חיבור Supabase – מדריך הקמה (פעם אחת)

## הדרך הקלה: לחיצה כפולה על `start-app.bat`
בתיקיית הפרויקט יש קובץ **start-app.bat**. לחיצה כפולה עליו:
1. בודקת ש־Node.js מותקן (אם לא – פותחת את דף ההורדה);
2. מתקינה/מעדכנת את הספריות כשצריך;
3. בפעם הראשונה בלבד שואלת על פרטי Supabase ושומרת אותם ב־`.env.local`:
   - **Session pooler URI** – Supabase → הפרויקט → **Connect** (למעלה) → **Session pooler** → העתקה;
   - **סיסמת מסד הנתונים** (שכחת? Project Settings → Database → Reset database password);
   - **Publishable key** אם עוד לא שמור;
4. יוצרת/מעדכנת את כל הטבלאות (schema.sql, chat.sql, people.sql) – רק כשהקבצים השתנו;
5. מפעילה את האפליקציה ומציגה ברקוד לסריקה.

- `start-app-tunnel.bat` – אותו דבר, כשהטלפון לא באותה רשת Wi‑Fi.
- `update-database.bat` – מריץ מחדש את כל קבצי מסד הנתונים (בטוח להריץ שוב).

השלבים הידניים למטה נשארים לגיבוי.

## 1. פתיחת פרויקט
1. נכנסים ל-https://supabase.com ונרשמים (אפשר עם GitHub או Google).
2. **New project** → שם: `instalearn` → בוחרים סיסמה למסד הנתונים (שומרים אותה) → Region: **Central EU (Frankfurt)** → **Create**.
3. מחכים כ-2 דקות עד שהפרויקט מוכן.

## 2. יצירת הטבלאות
1. בתפריט השמאלי: **SQL Editor** → **New query**.
2. מעתיקים את כל התוכן של הקובץ `supabase/schema.sql` ומדביקים.
3. לוחצים **Run**. אמור להופיע "Success".

## 3. חיבור האפליקציה
1. **Project Settings** → **API Keys** (או **Data API**).
2. מעתיקים את **Project URL** ואת ה-**Publishable key** (מתחיל ב-`sb_publishable_`).
3. בתיקיית הפרויקט יוצרים קובץ בשם `.env.local` ומדביקים:
   ```
   EXPO_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
   EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxxx
   ```

## 4. הגדרות התחברות
1. **Authentication** → **Sign In / Providers** → **Email**:
   בזמן פיתוח מומלץ לכבות את **Confirm email** – כך אפשר להירשם בלי לאשר מייל.
2. **Authentication** → **URL Configuration** → **Redirect URLs** → מוסיפים שתי שורות:
   ```
   exp://**
   learningapp://**
   ```

## 5. כניסה עם Google
1. נכנסים ל-https://console.cloud.google.com → יוצרים פרויקט חדש.
2. **APIs & Services** → **OAuth consent screen** → External → ממלאים שם אפליקציה ומייל → שומרים.
3. **Credentials** → **Create credentials** → **OAuth client ID** → סוג: **Web application**.
4. תחת **Authorized redirect URIs** מוסיפים:
   `https://<ה-Project-ID שלך>.supabase.co/auth/v1/callback`
5. מעתיקים את ה-**Client ID** וה-**Client secret**.
6. ב-Supabase: **Authentication** → **Sign In / Providers** → **Google** → Enable → מדביקים את שניהם → Save.

## 6. הרצה
```
npx expo install @supabase/supabase-js
npx expo start -c
```
באפליקציה יופיע מסך התחברות. נרשמים, והבחירות בעמוד Courses יישמרו בחשבון.

## 7. צ'אט (הודעות וקבוצות)
1. **SQL Editor** → **New query** → מדביקים את כל התוכן של `supabase/chat.sql` → **Run**.
   (אפשר להריץ שוב בלי בעיה. הקובץ יוצר טבלאות, הרשאות, חיבור בזמן אמת ותיקיית תמונות.)
2. מתקינים את ספריית בחירת התמונות ומפעילים מחדש:
   ```
   npx expo install expo-image-picker
   npx expo start -c
   ```
3. לבדיקה צריך שני משתמשים: נרשמים עם מייל נוסף (בטלפון אחר, או מתנתקים ונרשמים שוב),
   נותנים לכל אחד שם משתמש בעמוד הפרופיל, ומחפשים אחד את השני בלשונית Chats.

## 8. חיפוש משתמשים בצ'אט
1. **SQL Editor** → **New query** → מדביקים את כל התוכן של `supabase/people.sql` → **Run**.
   (אפשר להריץ שוב בלי בעיה.) הקובץ:
   - יוצר פרופיל לכל משתמש שאין לו (משתמשים שנרשמו לפני שהרצתם את schema.sql);
   - נותן שם (החלק של המייל לפני ה־@) לכל מי שאין לו שם;
   - מוסיף חיפוש לפי שם, ‎@username או **מייל מלא** (המייל עצמו לא נחשף למשתמשים אחרים).
2. בסוף ההרצה תופיע טבלה עם כל המשתמשים – כל שורה צריכה להכיל שם.
