import {getQuiz, sendResult} from "./axiosService.js";
import {renderImage} from "./components/image.js";
import {renderQuestion} from "./components/question.js";
import {renderQuestionResult} from "./components/questionResult.js";
import {getContactForm} from "./components/contactForm.js";
import {renderModal} from "./components/modal.js";


const itemImage = document.getElementById('item-image')
const quizSpace = document.getElementById('quiz-space')
const quizQuestions = document.getElementById('quiz-questions')
const quizIndicator = document.getElementById('quiz-indicator')
const quizResult = document.getElementById('quiz-results')
const btnNext = document.getElementById('btn-next')
const btnRestart = document.getElementById('btn-restart')
const formResult = document.getElementById('form-result')
const end = document.getElementById('end')

const quiz_id = localStorage.getItem('quiz_id')
let quiz = {}
let questions = []
let localResults = {}
let contacts = {}

getQuiz(quiz_id).then(function (result) {
    console.log(result);
    quiz = result;
    questions = quiz.questions
    quizPassing()
})

const quizPassing = () => {
    renderQuestionSpace(0)
    itemImage.innerHTML = renderImage('question')
}

const renderIndicator = (quizStep) => {
    quizIndicator.innerHTML = `${quizStep} из ${questions.length}`
}

const renderQuestionSpace = (index) => {
    renderIndicator(index + 1)
    quizQuestions.dataset.currentStep = index
    btnNext.disabled = true

    quizQuestions.innerHTML = renderQuestion(questions[index], index)
}

const renderResults = () => {
    itemImage.innerHTML = renderImage('result')
    let result = '<h2 class="title-results">Результаты прохождения квиза:</h2>'

    questions.forEach((question, index) => {
        result += renderQuestionResult(question, localResults[index])
    })
    quizResult.innerHTML = result
}


const renderFormResult = () => {
    formResult.innerHTML = `<h3>Теперь можно отправить ваши результаты составителю викторины</h3>` + getContactForm(quiz)
}

const sendResults = () => {
    let wholeResult = {}
    wholeResult['quiz'] = quiz_id
    let results = []
    for (const key in localResults) {
        const question = questions[key]
        const answer = question.answers.filter((answer) => answer.id === Number(localResults[key]))[0]
        const isCorrect = answer.is_correct ? ' (правильно)' : ' (неправильно)'
        results.push({question: question.number, answer: answer.text + isCorrect})
    }
    wholeResult['results'] = results
    if (Object.keys(contacts).length) {
        wholeResult['contacts'] = contacts
    }

    sendResult(wholeResult).then(function (res) {
        console.log(res);
        renderEnd(res)
    })
}

const renderEnd = (result) => {
    let endText = ''
    if (result === 'ok') {
        endText = 'Результаты отправлены. Спасибо за участие!'
    } else {
        endText = 'Что-то пошло не так. Но все равно спасибо за участие!'
    }
    end.innerHTML = renderModal(endText)
}

quizSpace.addEventListener('change', (event) => {
    if (event.target.classList.contains('answer-input')) {
        localResults[event.target.name] = event.target.value
        btnNext.disabled = false
    }
})

quizSpace.addEventListener('click', (event) => {
    if (event.target.classList.contains('btn-next')) {
        const nextQuestionIndex = Number(quizQuestions.dataset.currentStep) + 1
        if (nextQuestionIndex === questions.length) {
            quizQuestions.classList.add('questions--hidden')
            quizIndicator.classList.add('quiz--hidden')
            btnNext.style.visibility = 'hidden'
            quizResult.style.visibility = 'visible'
            btnRestart.style.visibility = 'visible'
            formResult.style.visibility = 'visible'
            renderResults()
            renderFormResult()
        } else {
            renderQuestionSpace(nextQuestionIndex)
        }
    } else if (event.target.classList.contains('btn-restart')) {
        localResults = {}
        quizResult.innerHTML = ''
        quizQuestions.classList.remove('questions--hidden')
        quizIndicator.classList.remove('quiz--hidden')
        btnNext.style.visibility = 'visible'
        quizResult.style.visibility = 'hidden'
        formResult.style.visibility = 'hidden'
        btnRestart.style.visibility = 'hidden'
        renderQuestionSpace(0)
        itemImage.innerHTML = renderImage('question')
    }
})

formResult.addEventListener('submit', (event) => {
    event.preventDefault();
    if (document.getElementById('name')) {
        contacts['name'] = document.getElementById('name').value
    }
    if (document.getElementById('email')) {
        contacts['email'] = document.getElementById('email').value
    }
    if (document.getElementById('phone')) {
        contacts['phone'] = document.getElementById('phone').value
    }
    sendResults()
})

end.addEventListener('click', (event) => {
    end.innerHTML = ''
})
