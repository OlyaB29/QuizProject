import {getQuizList} from "./axiosService.js";
import {renderQuizList} from "./components/quizList.js";
// import axios from 'axios';

const quizList = document.getElementById('quiz-list')


const renderQuizzes = () => {
    let quizzes = []

    getQuizList().then(function (result) {
        console.log(result);
        quizzes = result;
        quizList.innerHTML = `
                <ol class="quiz-list-ol">${renderQuizList(quizzes)}</ol>
            `
    })
}

renderQuizzes()
