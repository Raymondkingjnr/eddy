"""
Development seed for the updated Lesson Mentor models.

Creates:
- 2 users
- 4 lessons (2 per user)
- 3 topics per lesson
- Ordered topic sections and exercises
- Lesson notes and a sample exercise attempt

Run from the project root:
    python -m scripts.seed_lesson_mentor

The seed is intentionally non-destructive. It refuses to run if either seed
email already exists, so it will not silently duplicate or overwrite data.
Change the two development passwords before using this outside local development.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from fastapi_users.password import PasswordHelper
from sqlalchemy import select

from api.users import users
from config.db import async_session_maker, engine
from models.models import (
    ExerciseAttempt,
    Lesson,
    LessonNote,
    Topic,
    TopicExercise,
    TopicSection,
    User,
)

NOW = datetime.now(timezone.utc)
password_helper = PasswordHelper()

SEED_USERS = [
    {
        "email": "amara.okafor@example.com",
        "fullname": "Amara Okafor",
        "password": "password",
    },
    {
        "email": "daniel.eze@example.com",
        "fullname": "Daniel Eze",
        "password": "password",
    },
]


def make_section(
    position: int,
    kind: str,
    heading: str,
    body: str,
    key_idea: str | None = None,
    code_language: str | None = None,
    code: str | None = None,
) -> TopicSection:
    return TopicSection(
        position=position,
        kind=kind,
        heading=heading,
        body=body,
        key_idea=key_idea,
        code_language=code_language,
        code=code,
        created_at=NOW,
    )


def make_exercise(
    position: int,
    title: str,
    prompt: str,
    hint: str,
    solution: str,
    time_frame: int = 5,
) -> TopicExercise:
    return TopicExercise(
        position=position,
        title=title,
        prompt=prompt,
        hint=hint,
        solution=solution,
        time_frame=time_frame,
        created_at=NOW,
    )


def make_topic(
    position: int,
    title: str,
    description: str,
    time_frame: int,
    sections: list[TopicSection],
    exercises: list[TopicExercise],
    status: str = "not_started",
    completed_at: datetime | None = None,
) -> Topic:
    return Topic(
        title=title,
        description=description,
        time_frame=time_frame,
        position=position,
        status=status,
        completed_at=completed_at,
        embedding=None,
        created_at=NOW,
        sections=sections,
        exercises=exercises,
    )


def make_lesson(
    title: str,
    description: str,
    topics: list[Topic],
    status: str = "in_progress",
    source: str = "manual",
    completed_at: datetime | None = None,
) -> Lesson:
    # The lesson time_frame is always the sum of its topic time frames.
    return Lesson(
        title=title,
        description=description,
        time_frame=sum(topic.time_frame for topic in topics),
        status=status,
        source=source,
        completed_at=completed_at,
        embedding=None,
        created_at=NOW,
        updated_at=NOW,
        topics=topics,
    )


def build_lessons_for_amara() -> list[Lesson]:
    # Lesson 1: frontend development
    react_topics = [
        make_topic(
            1,
            "Understanding Components and JSX",
            "Learn how React components divide an interface into small, reusable pieces and how JSX describes the UI those components render.",
            25,
            [
                make_section(
                    1, "concept", "What is a React component?",
                    "A React component is a reusable unit of UI. It can represent a small element such as a button or a larger part of a page such as a navigation bar. Components receive data through props and return the interface React should display.",
                    "A component should have one clear responsibility and be reusable where the same UI is needed.",
                ),
                make_section(
                    2, "concept", "Writing JSX",
                    "JSX is a syntax extension that lets you describe UI with markup-like expressions inside JavaScript. JSX is transformed into JavaScript calls during the build process. A component must return a valid JSX expression, and sibling elements need a shared parent or fragment.",
                    "JSX looks like HTML, but it follows JavaScript and React rules.",
                ),
                make_section(
                    3, "example", "A reusable profile card",
                    "The ProfileCard component below accepts a name and role. Passing different props lets the same component display different people without duplicating its structure.",
                    "Use props to make a component configurable instead of hard-coding its content.",
                    "tsx",
                    "type ProfileCardProps = { name: string; role: string };\n\nfunction ProfileCard({ name, role }: ProfileCardProps) {\n  return (\n    <article className=\"profile-card\">\n      <h2>{name}</h2>\n      <p>{role}</p>\n    </article>\n  );\n}\n\n<ProfileCard name=\"Amara\" role=\"Frontend Developer\" />;",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Build a reusable component",
                    "Create a React component named CourseCard that accepts a course title and duration as props and displays both values.",
                    "Start by defining the props type, then destructure the props in the component parameters.",
                    "A valid solution defines a CourseCardProps type with title and duration fields, then returns JSX that renders both values.",
                    5,
                )
            ],
            status="completed",
            completed_at=NOW - timedelta(days=3),
        ),
        make_topic(
            2,
            "Props, State, and Events",
            "Understand the difference between data passed into a component and data managed by the component, then connect user actions to state updates.",
            30,
            [
                make_section(
                    1, "concept", "Props are inputs",
                    "Props allow a parent component to pass values to a child. A child should treat props as read-only. When a value needs to be changed, the component that owns that value should provide an appropriate callback.",
                    "Props flow from parent to child; a child does not directly mutate its props.",
                ),
                make_section(
                    2, "concept", "State changes over time",
                    "State stores information that can change while a component is being used, such as whether a menu is open or how many items are in a cart. The useState hook provides the current value and a setter that schedules a re-render.",
                    "Use state for values that affect what the component renders.",
                ),
                make_section(
                    3, "example", "A counter with an event handler",
                    "The button click calls the state setter. React then renders the component again with the updated count.",
                    "Event handlers describe what should happen in response to an interaction.",
                    "tsx",
                    "import { useState } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n\n  return (\n    <button onClick={() => setCount((current) => current + 1)}>\n      Count: {count}\n    </button>\n  );\n}",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Explain the data flow",
                    "A parent has a selectedTheme value and a child displays it. Should the child change the prop directly? Describe the correct approach.",
                    "Think about which component owns the state and how a child can notify its parent.",
                    "No. The child should not mutate the prop. The parent should own the state and pass a callback to the child if the child needs to request a change.",
                    5,
                )
            ],
            status="in_progress",
        ),
        make_topic(
            3,
            "Rendering Lists and Handling Forms",
            "Render collections with stable keys and manage form input so user-entered data can be validated and submitted.",
            35,
            [
                make_section(
                    1, "concept", "Rendering a collection",
                    "JavaScript map() can transform an array of data into an array of React elements. Each rendered item should have a stable key so React can match items between renders. Prefer a persistent identifier from the data over an array index when the list can change.",
                    "Keys help React identify which list item was added, removed, or changed.",
                ),
                make_section(
                    2, "concept", "Controlled form inputs",
                    "A controlled input receives its value from React state and updates that state through an onChange handler. This keeps the displayed value and application state in sync and makes validation and conditional UI easier to implement.",
                    "In a controlled input, React state is the source of truth for the field value.",
                ),
                make_section(
                    3, "example", "Rendering a list of courses",
                    "The example maps course records into list items and uses each course ID as its key.",
                    "Use stable IDs as keys when the underlying records have them.",
                    "tsx",
                    "type Course = { id: string; title: string };\n\nfunction CourseList({ courses }: { courses: Course[] }) {\n  return (\n    <ul>\n      {courses.map((course) => (\n        <li key={course.id}>{course.title}</li>\n      ))}\n    </ul>\n  );\n}",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Choose a suitable key",
                    "You are rendering a list of products. Each product has an id, name, and price. Which value should you use as the React key, and why?",
                    "Consider what happens when a product is inserted near the beginning of the list.",
                    "Use product.id because it is a stable identifier. An array index can point to a different product after items are inserted, removed, or reordered.",
                    5,
                )
            ],
        ),
    ]

    # Lesson 2: TypeScript foundations
    typescript_topics = [
        make_topic(
            1,
            "Primitive Types and Type Inference",
            "Learn how TypeScript describes common JavaScript values and infers types from initial assignments.",
            20,
            [
                make_section(
                    1, "concept", "Why types matter",
                    "TypeScript adds a static type system to JavaScript. It can detect many mistakes while code is being written or checked, before the application runs. Types also make function contracts and data structures easier to understand.",
                    "Types communicate what values a piece of code expects and produces.",
                ),
                make_section(
                    2, "concept", "Common primitive types",
                    "The most frequently used primitive types include string, number, and boolean. Arrays can be written as string[] or Array<string>. TypeScript can infer a variable's type from its initial value, so an annotation is not always necessary.",
                    "Use explicit annotations when they improve clarity or define an important boundary.",
                ),
                make_section(
                    3, "example", "Typed values and inference",
                    "The name variable is inferred as a string, while the function parameter and return type are explicitly documented.",
                    "Inference reduces repetitive annotations without removing type safety.",
                    "ts",
                    "const learnerName = \"Amara\";\nconst completedLessons: number = 3;\nconst isEnrolled: boolean = true;\n\nfunction greet(name: string): string {\n  return `Welcome, ${name}`;\n}",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Add the correct types",
                    "Declare a variable for a learner's email address, a variable for their score, and a variable indicating whether they passed.",
                    "Think about the kind of value each variable stores.",
                    "For example: const email: string = \"learner@example.com\"; const score: number = 82; const passed: boolean = true.",
                    4,
                )
            ],
            status="completed",
            completed_at=NOW - timedelta(days=1),
        ),
        make_topic(
            2,
            "Interfaces, Type Aliases, and Optional Properties",
            "Model the shape of application data with interfaces and type aliases, including fields that may not always be present.",
            30,
            [
                make_section(
                    1, "concept", "Describing object shapes",
                    "An interface describes the properties an object should have. A type alias can describe an object shape too, as well as unions, intersections, and other types. Both are useful for documenting the data that flows through an application.",
                    "Choose the construct that makes the intended data model easiest to read and maintain.",
                ),
                make_section(
                    2, "concept", "Optional and readonly properties",
                    "A question mark marks a property as optional, meaning an object may omit it. The readonly modifier prevents reassignment of that property through the declared type. These modifiers help communicate how data is expected to be used.",
                    "Optional means a property may be absent; it does not automatically mean its value is null.",
                ),
                make_section(
                    3, "example", "A learner profile type",
                    "The profile requires an ID and name, but bio is optional. A function can accept this shape and safely handle the optional field.",
                    "Model required and optional data explicitly.",
                    "ts",
                    "interface LearnerProfile {\n  readonly id: string;\n  name: string;\n  bio?: string;\n}\n\nfunction getProfileLabel(profile: LearnerProfile): string {\n  return profile.bio\n    ? `${profile.name}: ${profile.bio}`\n    : profile.name;\n}",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Design a course type",
                    "Create an interface for a course with a required id, title, and durationMinutes, plus an optional description.",
                    "Use string for text fields and number for the duration.",
                    "interface Course { id: string; title: string; durationMinutes: number; description?: string; }",
                    5,
                )
            ],
            status="in_progress",
        ),
        make_topic(
            3,
            "Union Types and Narrowing",
            "Represent values that can have more than one valid type and narrow those possibilities before using a value.",
            25,
            [
                make_section(
                    1, "concept", "Working with unions",
                    "A union type uses the vertical bar to say that a value may be one of several types. For example, an API identifier might be a string or a number. Code must account for the possible members of the union before using member-specific operations.",
                    "A union describes alternatives, not a value that is both types at once.",
                ),
                make_section(
                    2, "concept", "Narrowing a value",
                    "TypeScript narrows a union when code checks the value with tools such as typeof, equality checks, the in operator, or a discriminant property. After a successful check, TypeScript allows operations that are valid for the narrowed type.",
                    "Check which case you have before using operations specific to that case.",
                ),
                make_section(
                    3, "example", "Handling a string or number",
                    "The typeof check narrows the value so the function can safely choose the appropriate conversion.",
                    "Narrowing makes union types practical while preserving type safety.",
                    "ts",
                    "function formatId(id: string | number): string {\n  if (typeof id === \"number\") {\n    return `ID-${id.toFixed(0)}`;\n  }\n\n  return `ID-${id.toUpperCase()}`;\n}",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Narrow a union",
                    "Write a function formatValue that accepts string | number and returns a string. If the value is a number, return it with two decimal places; otherwise return the string in uppercase.",
                    "Use typeof value === \"number\" as the condition.",
                    "function formatValue(value: string | number): string { return typeof value === \"number\" ? value.toFixed(2) : value.toUpperCase(); }",
                    5,
                )
            ],
        ),
    ]

    return [
        make_lesson(
            "React Fundamentals: Building Reusable Interfaces",
            "A practical introduction to React components, JSX, props, state, events, lists, and forms. By the end, learners can structure a small interactive interface using reusable components.",
            react_topics,
            status="in_progress",
            source="manual",
        ),
        make_lesson(
            "TypeScript Foundations for Frontend Developers",
            "Build a strong TypeScript foundation by learning primitive types, object shapes, optional properties, unions, and type narrowing through practical frontend examples.",
            typescript_topics,
            status="in_progress",
            source="ai",
        ),
    ]


def build_lessons_for_daniel() -> list[Lesson]:
    # Lesson 1: SQL and relational database fundamentals
    sql_topics = [
        make_topic(
            1,
            "Tables, Rows, Columns, and Primary Keys",
            "Understand how relational databases organize information and how primary keys uniquely identify records.",
            25,
            [
                make_section(
                    1, "concept", "The relational table",
                    "A relational database stores data in tables. Each table represents an entity or relationship, each row represents one record, and each column represents an attribute. A well-designed table gives each column a clear meaning and an appropriate data type.",
                    "A table is a structured collection of records with a defined set of columns.",
                ),
                make_section(
                    2, "concept", "Primary keys",
                    "A primary key uniquely identifies each row in a table. It must be unique and cannot be null. A table usually has one primary key, which may consist of one column or multiple columns.",
                    "Use a primary key when other records need a reliable way to refer to a row.",
                ),
                make_section(
                    3, "example", "A users table",
                    "A users table can use an integer ID as its primary key while storing an email address and the date the account was created.",
                    "The primary key identifies the record independently of changeable display data.",
                    "sql",
                    "CREATE TABLE users (\n  id INTEGER PRIMARY KEY,\n  email VARCHAR(255) NOT NULL UNIQUE,\n  created_at TIMESTAMP NOT NULL\n);",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Identify the primary key",
                    "A books table contains id, title, author, and published_year. Which column is the best primary key and why?",
                    "A title may not be unique, and books can share an author or publication year.",
                    "The id column is the best choice if it is guaranteed to be unique and non-null. Titles and other descriptive fields may be duplicated or changed.",
                    5,
                )
            ],
            status="completed",
            completed_at=NOW - timedelta(days=4),
        ),
        make_topic(
            2,
            "Relationships and Foreign Keys",
            "Connect related records with foreign keys and recognize one-to-one, one-to-many, and many-to-many relationships.",
            30,
            [
                make_section(
                    1, "concept", "What a foreign key does",
                    "A foreign key is a column or set of columns that references a candidate key, commonly the primary key, in another table. It helps enforce referential integrity so a record cannot refer to a related record that does not exist, subject to the configured database rules.",
                    "Foreign keys represent and protect relationships between tables.",
                ),
                make_section(
                    2, "concept", "Common relationship types",
                    "In a one-to-many relationship, one parent record can be related to many child records. A many-to-many relationship is commonly implemented with a junction table containing foreign keys to both related tables. A one-to-one relationship usually adds a uniqueness constraint to the foreign key.",
                    "The relationship type determines where foreign keys and constraints belong.",
                ),
                make_section(
                    3, "example", "Users and orders",
                    "Each order belongs to one user, while a user may have many orders. The user_id column on orders references the users table.",
                    "Place the foreign key on the many side of a one-to-many relationship.",
                    "sql",
                    "CREATE TABLE orders (\n  id INTEGER PRIMARY KEY,\n  user_id INTEGER NOT NULL,\n  total_amount DECIMAL(10, 2) NOT NULL,\n  FOREIGN KEY (user_id) REFERENCES users(id)\n);",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Model a one-to-many relationship",
                    "A school has many students, but each student belongs to one school. Which table should contain the foreign key?",
                    "Find the side that can contain many records for one parent.",
                    "The students table should contain school_id as a foreign key referencing schools.id.",
                    5,
                )
            ],
            status="in_progress",
        ),
        make_topic(
            3,
            "Writing SELECT Queries and Filtering Data",
            "Retrieve records with SELECT, choose specific columns, filter rows with WHERE, and sort results with ORDER BY.",
            30,
            [
                make_section(
                    1, "concept", "Selecting data",
                    "SELECT retrieves data from one or more tables. You can select every column with an asterisk or list only the columns needed by the application. Selecting only required columns can make query intent clearer and reduce unnecessary data transfer.",
                    "Prefer listing the columns your query actually needs.",
                ),
                make_section(
                    2, "concept", "Filtering and sorting",
                    "WHERE filters rows based on a condition. ORDER BY sorts the returned rows in ascending or descending order. Multiple conditions can be combined with AND and OR, and parentheses help make complex conditions explicit.",
                    "WHERE controls which rows are returned; ORDER BY controls their order.",
                ),
                make_section(
                    3, "example", "Finding active learners",
                    "This query returns the names and email addresses of active learners, with the newest accounts first.",
                    "Filtering and sorting are separate operations that can be used together.",
                    "sql",
                    "SELECT fullname, email\nFROM users\nWHERE is_active = TRUE\nORDER BY created_at DESC;",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Write a filtered query",
                    "Write a query that selects title and duration_minutes from lessons where duration_minutes is greater than 30, ordered from longest to shortest.",
                    "Use WHERE for the duration condition and ORDER BY with DESC for descending order.",
                    "SELECT title, duration_minutes FROM lessons WHERE duration_minutes > 30 ORDER BY duration_minutes DESC;",
                    5,
                )
            ],
        ),
    ]

    # Lesson 2: Python backend fundamentals
    python_topics = [
        make_topic(
            1,
            "Python Variables, Data Types, and Collections",
            "Review Python's core data types and learn when to use lists, tuples, dictionaries, and sets in backend applications.",
            25,
            [
                make_section(
                    1, "concept", "Variables and basic types",
                    "A Python variable is a name bound to an object. Common built-in types include int, float, str, and bool. Python is dynamically typed, but type annotations can document expected values and support static analysis tools.",
                    "A variable name refers to an object; a type describes the kind of value that object represents.",
                ),
                make_section(
                    2, "concept", "Choosing a collection",
                    "Lists are ordered and mutable, tuples are ordered and immutable, dictionaries store key-value mappings, and sets store unique elements. Choosing the right collection makes operations and intent clearer.",
                    "Choose a collection based on ordering, mutability, lookup, and uniqueness requirements.",
                ),
                make_section(
                    3, "example", "A dictionary for a user",
                    "A dictionary can represent a small record with named fields. In a larger application, a dedicated model or schema may provide stronger validation and clearer structure.",
                    "Dictionaries are useful for mapping named keys to values.",
                    "python",
                    "user = {\n    \"id\": 101,\n    \"fullname\": \"Daniel Eze\",\n    \"is_active\": True,\n}\n\nprint(user[\"fullname\"])",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Choose the right collection",
                    "You need to store unique permission names and quickly check whether a permission exists. Which built-in collection is a good fit?",
                    "The requirement says duplicate values should not be stored.",
                    "A set is a good fit because it stores unique values and supports efficient membership checks.",
                    5,
                )
            ],
            status="completed",
            completed_at=NOW - timedelta(days=2),
        ),
        make_topic(
            2,
            "Functions, Parameters, and Return Values",
            "Write small reusable functions, pass information through parameters, and return values to the calling code.",
            25,
            [
                make_section(
                    1, "concept", "Defining a function",
                    "The def keyword defines a function. Parameters name the inputs a function accepts, while the return statement sends a result back to the caller. A function without an explicit return statement returns None.",
                    "A function should have a clear purpose, inputs, and expected output.",
                ),
                make_section(
                    2, "concept", "Default and keyword arguments",
                    "Default parameter values make some arguments optional. Keyword arguments identify values by parameter name at the call site, which can improve readability when a function accepts several parameters.",
                    "Use defaults for genuinely optional behavior and keyword arguments for clarity.",
                ),
                make_section(
                    3, "example", "A reusable calculation",
                    "This function calculates a discounted price and returns the result. Its parameters make it reusable for different prices and discount rates.",
                    "Return a result when callers need to use the function's calculation.",
                    "python",
                    "def discounted_price(price: float, discount: float = 0.10) -> float:\n    return price * (1 - discount)\n\nfinal_price = discounted_price(100, discount=0.15)\nprint(final_price)",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Write a reusable function",
                    "Write a function called calculate_total that accepts price and quantity and returns their product. Include type annotations.",
                    "The result is a number, and both inputs should be numeric.",
                    "def calculate_total(price: float, quantity: int) -> float: return price * quantity",
                    5,
                )
            ],
            status="in_progress",
        ),
        make_topic(
            3,
            "Exceptions and Safe Error Handling",
            "Understand runtime exceptions and handle expected failures without hiding unexpected programming errors.",
            30,
            [
                make_section(
                    1, "concept", "What an exception means",
                    "An exception signals that an operation could not proceed normally. Examples include converting invalid text to an integer, opening a missing file, or accessing a missing dictionary key. If an exception is not handled, it can propagate up the call stack.",
                    "Exceptions represent exceptional control flow and should be handled deliberately.",
                ),
                make_section(
                    2, "concept", "try, except, and finally",
                    "A try block contains code that may raise an exception. An except block handles a matching exception type. A finally block runs whether an exception occurred or not, making it useful for cleanup. Catch specific exceptions when possible.",
                    "Avoid broad exception handling that hides bugs or makes failures impossible to diagnose.",
                ),
                make_section(
                    3, "example", "Validating numeric input",
                    "The function catches the expected ValueError and returns a clear result for invalid input rather than allowing that specific conversion failure to crash the caller.",
                    "Handle the failure you expect and allow unrelated errors to remain visible.",
                    "python",
                    "def parse_age(value: str) -> int | None:\n    try:\n        age = int(value)\n    except ValueError:\n        return None\n\n    if age < 0:\n        return None\n    return age",
                ),
            ],
            [
                make_exercise(
                    1,
                    "Handle a conversion error",
                    "A function converts a string to an integer. Which exception should it catch if the string is not a valid integer?",
                    "Consider the exception raised by int(\"hello\").",
                    "Catch ValueError, which is raised when int() receives a string that cannot be parsed as an integer.",
                    5,
                )
            ],
        ),
    ]

    return [
        make_lesson(
            "Relational Database Fundamentals with SQL",
            "Learn how relational databases organize data, enforce relationships, and retrieve records. The lesson covers table design, primary keys, foreign keys, and practical SELECT queries.",
            sql_topics,
            status="in_progress",
            source="manual",
        ),
        make_lesson(
            "Python Foundations for Backend Development",
            "Build practical Python fundamentals for backend work, including data types, collections, functions, return values, and safe exception handling.",
            python_topics,
            status="in_progress",
            source="ai",
        ),
    ]


async def seed() -> None:
    async with async_session_maker.begin() as session:
        existing_emails = set(
            (
                await session.scalars(
                    select(User.email).where(
                        User.email.in_([user["email"] for user in SEED_USERS])
                    )
                )
            ).all()
        )

        if existing_emails:
            raise RuntimeError(
                "Seed users already exist: "
                + ", ".join(sorted(existing_emails))
                + ". Remove or change those records before running this seed again."
            )

        users: list[User] = []
        for user_data in SEED_USERS:
            users.append(
                User(
                    email=user_data["email"],
                    fullname=user_data["fullname"],
                    hashed_password=password_helper.hash(
                        user_data["password"]),
                    is_active=True,
                    is_superuser=False,
                    is_verified=True,
                    lessons=[],
                )
            )

        users[0].lessons.extend(build_lessons_for_amara())
        users[1].lessons.extend(build_lessons_for_daniel())

        session.add_all(users)
        await session.flush()

        # Add a note and a sample exercise attempt for every lesson.
        # Uses foreign keys instead of lesson.notes (lazy="raise").
        for user in users:
            for lesson in user.lessons:
                first_topic = lesson.topics[0]

                session.add(
                    LessonNote(
                        lesson_id=lesson.id,
                        topic_id=first_topic.id,
                        content=(
                            f"Study note: Revisit '{first_topic.title}' and explain "
                            "the main idea in your own words before moving on."
                        ),
                        created_at=NOW,
                        updated_at=NOW,
                    )
                )

                if first_topic.exercises:
                    exercise = first_topic.exercises[0]

                    session.add(
                        ExerciseAttempt(
                            exercise_id=exercise.id,
                            answer=(
                                "Sample seeded attempt: this response demonstrates "
                                "how an exercise submission is stored."
                            ),
                            is_correct=True,
                            feedback=(
                                "This is sample development data. Replace this "
                                "attempt with a real learner submission when testing."
                            ),
                            created_at=NOW,
                        )
                    )

        print("Seed data inserted successfully.")
        print(f"Users: {len(users)}")
        print(f"Lessons: {sum(len(user.lessons) for user in users)}")
        print(
            "Topics: "
            + str(
                sum(
                    len(lesson.topics)
                    for user in users
                    for lesson in user.lessons
                )
            )
        )
        print(
            "Topic sections: "
            + str(
                sum(
                    len(topic.sections)
                    for user in users
                    for lesson in user.lessons
                    for topic in lesson.topics
                )
            )
        )
        print(
            "Exercises: "
            + str(
                sum(
                    len(topic.exercises)
                    for user in users
                    for lesson in user.lessons
                    for topic in lesson.topics
                )
            )
        )


async def main() -> None:
    engine.echo = False
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
