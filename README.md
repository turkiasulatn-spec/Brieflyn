<img width="1152" height="736" alt="image" src="https://github.com/user-attachments/assets/31892d24-3c53-4644-bbeb-09dfc19848a0" />

# Brieflyn - Smart Personalized News Aggregator with AI Chat

#### Video Demo: <URL HERE>
#### GitHub Username: <YOUR_GITHUB_USERNAME>
#### edX Username: <YOUR_EDX_USERNAME>
#### City and Country: <YOUR_CITY, YOUR_COUNTRY>
#### Date: <RECORDING_DATE>

---

## Description

### What Is This Project?

So I built Brieflyn because I was honestly tired of jumping between ten different news sites every morning just to find stories I actually care about. The idea is simple: you sign up, tell the app what language you speak and what topics you're into, and it gives you a personalized news feed pulled from multiple sources. No more endless scrolling through headlines about things you couldn't care less about.

But here's the thing that really got me excited. You know how sometimes you read an article and you're thinking "wait, what does this actually mean?" or "I wonder how this connects to that other thing I read yesterday?" So I built this feature where you can literally open a chat window and talk to the article. You ask questions, the article answers. It's like having someone knowledgeable sitting next to you while you read, except it's actually the AI processing the article's content and having a conversation with you about it. This isn't some mockup or placeholder—when you provide your API key during registration (you can choose between OpenAI, Google, or Groq), the app uses that to power real conversations with your articles.

### How It Works

Let me walk you through the flow. When someone lands on the site, they've got two options: register or log in. The registration form asks for the usual stuff like username, email, password, but also asks for your language preference, country, which AI provider you want to use, and your API key for that provider. I know asking for an API key during signup might seem unusual, but here's why I did it: this way, every user gets their own personalized AI experience without me having to foot a massive API bill. Users bring their own keys, and the app uses those keys to power the chat feature specifically for them.

Once you're logged in, the dashboard pulls news based on the language you selected during registration. I'm using a third-party news API to fetch articles—right now the default topic is technology, but the system is built to support any topic passed through the URL. Each article appears as a card with the image, title, and two buttons: one takes you to the original article on its source website, and the other opens that chat window I mentioned.

The search bar at the top of the dashboard was a deliberate choice. Instead of making a server request every time you type something, I wrote it in pure JavaScript to filter articles right in your browser. The article titles are stored in data attributes on each card, and the script just checks if what you typed matches any part of the title. It's instant—you type "AI" and any article with AI in the title stays visible while the rest disappear. No loading spinners, no waiting. I really wanted the browsing experience to feel snappy.

### The Files

Let me explain what each file does and why I structured things this way.

**app.py** is where everything comes together. Flask handles the routing, session management, and database interactions. I set up a `login_required` decorator that checks if there's a user_id in the session before letting anyone access the dashboard. If someone tries to go to /dashboard without being logged in, they get redirected to the login page. Same thing works in reverse—if you're already logged in and try to visit /login or /register, the app just sends you straight to the dashboard. That was actually a bug I discovered during testing: I logged in, manually typed /login in the URL bar, and realized the app happily showed me the login form again, which makes no sense for someone who's already authenticated. Fixed that with a simple check at the top of both routes.

The database connection lives in a function called get_db(). It creates the db folder automatically if it somehow doesn't exist, connects to the SQLite file, and sets row_factory so I get dictionary-like rows instead of tuples. Much easier to work with when you're passing data to templates.

For password security, I'm using Werkzeug's hashing. Passwords get hashed before they ever touch the database, and during login, the submitted password gets checked against the stored hash. Plain text passwords are never stored anywhere. That was non-negotiable for me.

**db/database.db** is the SQLite database. The users table stores everything: username, email, hashed password, language, country, API key, API provider choice, role (defaults to 'user'), and a creation timestamp. The API provider column has a CHECK constraint so only 'openai', 'google', or 'groq' can be inserted. That's a small thing but it prevents garbage data from getting in if someone messes with the form.

**templates/auth/register.html** is the registration form. It extends a base layout template and I kept the styling consistent with the original design—those arrow SVGs, the circle backgrounds, the card layout. The form collects all the fields the database expects. If someone tries to register with an email that's already in the system, the app catches it, queries the database, and sends back an error message rendered right on the same page. They don't lose their form data or get redirected somewhere confusing.

**templates/auth/login.html** is simpler. Email and password fields, a "Remember me" checkbox (though honestly that's more of a UI comfort thing right now since the session already persists), and a link to the registration page. If login fails—wrong email or password—it shows an error. If it succeeds, session gets populated with the user's info and off they go to the dashboard.

**templates/dashboard.html** is the big one. This is where users actually spend their time. The layout uses a sidebar navigation that I kept from the original design—it's got links for Dashboard, My Feed, AI Assistant, Interests, Saved items, Notifications, Sources, Insights, Settings, and Sign Out. Not all of those are functional yet, but the structure is there for future development. The main content area shows news articles in a responsive grid.

Each article card has two buttons at the bottom. "View Article" opens the original source in a new context. "Chat with Article" opens a popup in the bottom-right corner of the screen. I styled that popup with a dark theme and a gradient header because I wanted it to feel distinct from the rest of the dashboard—like you're stepping into a conversation space rather than just reading. When it opens, it displays the article's title and description as the starting context, and you can type questions. The JavaScript for the chat buttons was actually something I had to fix. At first I was using inline onclick attributes with Jinja template variables, and only the first article's button worked because of how the loop was rendering. I switched to data attributes on each article card and added event listeners after DOM content loads. Now every single "Chat with Article" button correctly opens the popup with that specific article's content.

The search functionality is client-side JavaScript. Each article card stores its lowercase title in a data-title attribute, and when you type in the search bar, the script loops through all cards and toggles visibility based on whether the search term appears in the title. The whole thing happens in the browser—zero server requests.

**templates/layouts/base.html and admin.html** are the wrapper templates. Base layout is for the public pages, admin layout is for the dashboard. They include all the CSS, JavaScript, and structural elements that every page needs. This avoids code duplication and makes it easy to change the overall look of the site by editing just one file.

### Design Decisions I Made

The API key approach was a big one. Most sites that offer AI features just eat the API costs themselves or charge a subscription. I went with "bring your own key" because it makes the project sustainable for anyone to run without ongoing costs. During registration, you pick your provider and paste your key. That key gets stored in the database and can be used to power real conversations with articles through the LLM of your choice. It also means users aren't locked into one AI provider—you can use OpenAI if you want GPT, Google if you prefer Gemini, or Groq if you want something else.

Language support was important to me because not everyone consumes news in English. When a user registers and picks Arabic, the dashboard requests Arabic-language articles from the news API. That language preference is stored in the database and queried fresh each time the dashboard loads, so it always stays in sync with what the user chose.

I chose server-side sessions over JWT tokens because Flask's session system is dead simple and works perfectly with template rendering. There's no need for the complexity of token refresh or storing tokens in local storage when the built-in session cookie does exactly what I need.

The search being client-side was an intentional performance choice. News APIs often have rate limits or per-request costs, so I didn't want to fire off a new API call every time someone types a character. Instead, the API call happens once when the dashboard loads, and then the user can filter through those results instantly. It's faster for the user and more efficient for the API.

### Tech Stack

The backend is Python with Flask. I used SQLite3 for the database because it requires zero configuration and works perfectly for a project of this scale. Werkzeug handles password hashing. The frontend is HTML, CSS with Bootstrap, and vanilla JavaScript—no React or Vue, just straightforward DOM manipulation.

The news comes from a third-party news API, and the AI chat feature connects to whichever LLM provider the user selected during registration.

### How to Get It Running

Make sure you have Python installed, then:

1. Clone the project or download the files
2. Install Flask and the other dependencies: `pip install flask requests werkzeug`
3. Run the app: `python app.py`
4. Open your browser to `http://127.0.0.1:5000`
5. Create an account, enter your API key for your preferred AI provider, and start browsing news in your language

### What I'd Add Next

The sidebar has links for Interests, Saved, and other features that aren't wired up yet. The next step would be letting users select specific topics they care about and having those topics drive the news feed. Bookmarking articles would be straightforward with another database table. The AI chat could be expanded to handle follow-up questions and maintain conversation context across multiple messages about the same article. Email digests would be great too—a daily summary of top stories in your topics, delivered to your inbox.

This project was genuinely fun to build. It started as a way to solve my own frustration with news browsing and turned into something I could see myself actually using every day. Hope you find it useful too.
