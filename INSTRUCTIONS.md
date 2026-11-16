# Technical Take-Home Assignment: Candidate Submission Guidelines

Welcome, and thank you for taking the time to participate in our technical evaluation process.

This document explains how to approach, complete and submit your take-home assignment.

## 1. Read the assignment

Start by reading the complete assignment document: **[RoomBook: Take-Home Assignment](ASSIGNMENT.md)**.

It includes:

- Problem statement and application overview
- Technical requirements and business rules
- Individual tasks and expected outcomes
- Testing requirements
- Documentation requirements
- GitHub submission instructions

Please read the entire document before starting. The setup commands for the starter app are in [README.md](README.md).

## 2. Repository setup

You must create your own **private** GitHub repository for the solution.

Important:

- Do **not** fork this repository.
- Do **not** open pull requests against this repository.
- Do **not** submit your solution in a public repository.
- Create a separate **private** repository under your GitHub account.
- Push the provided starter code (this repository's `main`) into your private repository.
- Add the designated reviewer as a collaborator with **read** access. The hiring team will tell you their GitHub username.

Repository naming suggestion: `roombook-<your-name>`

```bash
git clone https://github.com/chemours-app-dev/take_home_test roombook && cd roombook
git remote set-url origin <your private repo URL>
git push -u origin main
```

## 3. Development approach and tools

You are free to choose your preferred development workflow. You may:

- Write code manually
- Use AI coding assistants or agents
- Use IDE-integrated AI tools
- Use command-line coding agents
- Combine manual development with AI assistance

Examples include Cursor, GitHub Copilot, Claude Code, ChatGPT, or other tools you prefer.

**There is no restriction on using AI tools.** We are interested in how you approach problems, make technical decisions, validate solutions, and take ownership of the code you submit.

Please document your AI tool usage transparently, in `DECISIONS.md` and in each pull request description, including:

- Which tools you used
- Which tasks you used them for
- At least one instance where an AI suggestion was incorrect or you rejected its recommendation, and why

## 4. Task-wise development and pull requests

Follow the task-wise branch and pull request workflow described in [ASSIGNMENT.md](ASSIGNMENT.md). Open the pull requests against your private repository's `main` branch, in this order:

| PR | Branch (suggested) | Contains |
|---|---|---|
| 1 | `fix/back-to-back-bookings` | Task 1: the fix, its test, and `DECISIONS.md` |
| 2 | `feat/suggest-slots` | Task 2: the `/suggest` endpoint and its tests |
| 3 | `feat/prevent-double-booking` | Task 3: the double-booking guard |
| 4 | `feat/find-slot-ui` | Task 4: the React form |

Each task should have:

- A separate feature/fix branch
- A dedicated pull request
- Meaningful commits showing your development progress
- A brief PR description covering what changed and why, how to test it, and how you used AI

Merge each completed PR into `main` **before** starting the next task. Use a normal merge commit, **not** squash, so we can see your commits.

Please do not squash a whole task into a single commit. We would like to understand your development process and incremental changes.

## 5. Documentation and testing

Please ensure that:

- Your application can be set up and run locally
- Tests are included for the implemented functionality and run with one command (for example `pytest`)
- Existing functionality is not unnecessarily broken
- `README.md` contains relevant setup and execution instructions
- `DECISIONS.md` documents assumptions, trade-offs, technical decisions, identified issues, and AI tool usage

If you cannot complete a task within the allotted time, open the unfinished PR as a **draft**, and document what remains and your proposed next steps.

## 6. Submission process

Once you have completed the assignment:

1. Make sure all relevant branches and pull requests are available in your private repository.
2. Merge completed pull requests into `main`.
3. Verify that your `README.md` and `DECISIONS.md` are included.
4. Make sure the designated reviewer has access to the repository.
5. Send the private GitHub repository URL to the hiring team.

## 7. Time allocation

The assignment has an expected time box of **3-4 hours**. Please stop at 4 hours. We do not expect every candidate to complete every task perfectly.

We value:

- Problem-solving ability
- Code quality and maintainability
- Understanding of backend and frontend concepts
- Database design and concurrency handling
- Testing and debugging practices
- Technical decision-making
- Ability to explain and take ownership of your implementation

## 8. Follow-up technical discussion

After reviewing your submission, we will schedule a **60-minute technical discussion**. During this discussion, you will be expected to:

- Walk us through your implementation
- Explain important technical decisions and trade-offs
- Discuss challenges you encountered
- Run the application and tests locally
- Make a few small changes to the code live, on screen share

Please make sure your development environment is ready and the application runs locally.

---

**Final note:** This exercise is intended to understand your engineering approach, not just the final output. Use the tools and workflow you are most comfortable with, work within the allotted time, and be prepared to explain the decisions behind your implementation.

Good luck!

Hiring Team
