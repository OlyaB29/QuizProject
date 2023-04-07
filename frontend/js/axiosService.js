const API_URL = 'http://localhost:8000/api';

export function getQuizList () {
	    const url = `${API_URL}/quizzes/`;
	    return axios.get(url).then(response => response.data);
    }

export function getQuiz (id) {
	    const url = `${API_URL}/quizzes/${id}/`;
	    return axios.get(url).then(response => response.data);
    }

export function sendResult (wholeResult) {
	    const url = `${API_URL}/results/`;
	    return axios.post(url, wholeResult).then(response => response.data);
    }


