export const renderQuizList  = (quizzes) =>
    quizzes.map((quiz) => `
            <li>                
                <a class="quiz-title" id=${quiz.id} onclick="localStorage.setItem('quiz_id',event.target.id)" 
                href="quiz.html">${quiz.title}</a>              
            </li>
            `
    )
        .join('')
