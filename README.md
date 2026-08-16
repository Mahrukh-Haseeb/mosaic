## Inspiration

Notice how every wellness app treats your wellbeing as a collection of separate pieces? Your sleep, your diet, your workouts... tracked individually, as if they are not dependent, not a mosaic.
But your body doesn't work that way. That's our _why_ behind **MOSAIC: the symbiosis of your body,  digitally**!
 
## What it does

MOSAIC lets users build a 3d wellness world combining all health scores. Key life factors like sleep, stress, relationships and fun are visual elements in that world!
What makes our project special is that each user deserves to know how everything connects in their body. That's why MOSAIC uses AI to explain hidden connections, i.e. how poor sleep + little daylight + inactivity affect energy. So when a user adjusts one factor, they see the whole ecosystem react; when a piece moves, the whole mosaic changes!
Rather than simply tracking health factors, MOSAIC combines health education, wellness actions and mindfulness altogether!

## How we built it
MOSAIC was built keeping one idea in mind, which is; instead of treating sleep, stress, 
movement, relationships and other parts of wellbeing as completely separate numbers, we 
wanted to see how they affect each other. 
We split the project into three main parts: the frontend, the backend/database, and the AI 
engine. 
### Storing the user's wellness data 
We used Supabase with PostgreSQL as the main database. It has tables storing user 
profiles, daily check-ins, goals, habits, detected patterns and what-if simulations. 
Each check-in contains factors such as sleep, nutrition, movement, stress, relationships, 
environment, fun, energy, mood and screen time. 
We also added authentication and row-level security(RLS) so that user-specific data is 
separated properly. 
The AI backend connects to the same Supabase database and then fetches a user's 
historical check-ins when it needs to analyse their data. 
### Finding connections between wellness factors 
This is where the main AI/ML part of MOSAIC comes in. 
We created a PatternDetector that takes a user's historical check-ins and calculates 
correlations between the different wellness factors. 
For example, if the user's sleep and energy tend to increase together, the system can 
identify that as a positive relationship. Similarly, if stress increases when sleep decreases, it 
can identify a negative relationship. 
We use Pearson correlation to calculate these relationships. Connections above a certain 
correlation threshold are treated as potentially meaningful patterns. The system also labels 
the relationship as positive or negative and gives it a strength like moderate or strong. 
We also added basic trend detection. The system looks at factors such as energy, stress and 
mood across different days of the week and identifies patterns such as a perfectly good or 
bad day. 
### The What-If simulator 
One of the main things we wanted MOSAIC to do differently from a normal wellness tracker 
was let the user “actually experiment”. 
The What-If simulator takes the user's historical data and calculates what could happen if 
one factor changes. 
For example: _"What if I increase my sleep from 5 hours to 7 hours?"_
The simulator looks at the user's existing averages and the correlations between their 
factors. It then estimates how the other factors could change based on that relationship. 
We also calculate a wellness score before and after the change so the user can see the 
overall effect of the simulated change. 
This isn't intended to be a medical prediction but an interactive way of showing users how 
changes in one part of their routine can precisely affect the rest of their wellness ecosystem. 
### Turning the data into useful advice 
Once the pattern detector finds connections, we pass the user's averages and the detected 
patterns to Google Gemini. 
Instead of asking Gemini for generic wellness advice, we give it the user's actual data. 
The prompt asks Gemini to generate five personalized and actionable insights, reference the 
user's actual numbers, focus on connections between factors, and keep the advice 
encouraging and non-judgmental. 
For example, instead of simply saying: _"Get more sleep."_ 
MOSAIC can generate advice based on the user's own combination of sleep, stress, 
movement and other factors. 
This makes the AI output feel more like a reflection of the user's own habits rather than a 
generic health tip. 
### FastAPI as the AI backend 
We used FastAPI to expose the AI functionality through REST endpoints. 
The main endpoints handle: 
- Pattern detection 
- What-If simulations 
- Personalized insights 
The FastAPI server fetches the user's data from Supabase, passes it through the 
appropriate AI module, and returns the result to the frontend. 
We used Uvicorn to run the FastAPI application. 
The project dependencies include FastAPI, Uvicorn, Pandas, NumPy, SciPy, scikit-learn, 
Supabase and Google's Gemini SDK. 
### Handling missing data and development 
Since we were building the project during a hackathon, we also added a mock-data fallback. 
If Supabase isn't available or a user doesn't have enough check-in data yet, the AI backend 
can generate sample wellness data and continue running. 
### Connecting everything together 
The final flow is as follows: 
```text
User 
↓ 
MOSAIC Frontend 
↓ 
Backend APIs 
↓ 
Supabase PostgreSQL 
↓ 
User's wellness history 
↓ 
AI Engine 
├── Pattern Detection 
├── Trend Detection 
├── What-If Simulation 
└── Gemini Insights 
↓ 
Results shown in the 3D wellness world 
```
The important part is that the AI isn't working on isolated numbers. It uses the user's history 
to find relationships between multiple factors and then turns those relationships into 
something the user can actually understand and act on. 

## Tech Stack

| Part | Technology | Why we used it |
|---|---|---|
| Frontend | HTML, CSS, JavaScript / 3D UI | Interactive wellness world |
| AI Backend | FastAPI | Lightweight REST API for AI features |
| Server | Uvicorn | Runs the FastAPI application |
| Database | Supabase / PostgreSQL | Stores user wellness history and application data |
| Authentication | Supabase Auth | User authentication |
| Data Analysis | Pandas + NumPy | Processing wellness history |
| Correlation Analysis | SciPy / Pearson correlation | Finding relationships between wellness factors |
| ML Ecosystem | scikit-learn | Supporting the ML and data-analysis stack |
| Generative AI | Google Gemini API | Personalized wellness insights |
| Version Control | Git + GitHub | Team collaboration and version control |
| Backend Deployment | Railway | Hosting the FastAPI server |
| Frontend Deployment | Vercel | Hosting the frontend |

## Why We Chose This Approach 
We didn't want MOSAIC to become another app where a user sees: 
_Sleep: 65_ 
_Stress: 72_ 
_Movement: 48_ 
and is left wondering what those numbers actually mean. 
Instead, we wanted the system to answer the next question: _"How are these things connected?"_
That's why the backend keeps the user's history rather than only looking at their latest 
check-in. This history gives us enough information to find relationships, identify trends and 
let the user experiment with possible changes. 
The Gemini layer then turns those numbers and relationships into language that is easier for 
a normal user to understand. 

## Challenges we ran into

### Collaborating in different timezones
With team members in different locations, finding overlasping hours for live collaboration, quick debugging, and even ideation was difficult. We had to rely on asyncw communication, task splitting and check-ins to keep our momentum.

### Combining many wellness dimensions into one coherent design
Sleep, nutrition, relationships, fun, movement, stress and environment are the key factors of MOSAIC. Not separating them meant we had to design a single coherent visual language so as not to create any confusion for users.

## Accomplishments that we're proud of

We coordinated across 3 different time zones, syncing up at odd hours to push code and ship a fully functional AI-powered wellness app. We launched a live backend on Railway, a frontend on Vercel, a Supabase database storing real user data, and an AI that gives personalized, actionable insights. Everything is connected and working. We failed fast, fixed faster. From Vercel timeouts to Railway build errors, we hit every wall and kept going. We didn't give up. We built a 3D ecosystem (Three.js) because visualizing wellness as a system shouldn't feel like a hospital dashboard. We gave users a "Now What?". Our What-If simulator and micro-actions (breathing, movement, hydration) turn insights into action so users don't just see their wellbeing but they can actually improve it.

## What we learned

Building MOSAIC showed us that the difficult part of an AI product isn't always the model 
itself. A lot of the work is in getting the data flow right. 
We had to think about how the data is collected, stored, processed, analysed and finally 
presented back to the user. 
We also learned that AI works much better in this type of application when it is given 
structured, user-specific information instead of being asked to generate advice from nothing. 

## What's next for MOSAIC
The current version focuses on showing relationships between wellness factors and allowing 
users to experiment with changes. 
Going forward, MOSAIC could become more personalised by learning from longer-term user 
behaviour, improving the prediction model behind the What-If simulator, and making the 3D 
wellness world react even more dynamically to changes in the user's data! 

##  Use of AI
### AI Models
Gemini 3.6 Flash (free tier)
XGBoost (scikit-learn): Pattern detection and correlation analysis between wellness factors    (open-source & free)
scikit-learn: Machine learning for trend detection   
(open-source & free)
We send the detected patterns and user averages to Gemini with this prompt:
"Based on this user's weekly wellness data, generate 5 personalized, actionable insights. Be specific and reference their actual data. Be encouraging and non-judgmental. Focus on connections between factors."
