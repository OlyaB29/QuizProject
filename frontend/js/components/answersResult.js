export function renderAnswersResult (answers, localResult) {

    const checkIsCorrect = (answer) => {
        let className = ''

        if (!answer.is_correct && answer.id === Number(localResult)) {
            className = 'answer-invalid'
        } else if (answer.is_correct) {
            className = 'answer-valid'
        }

        return className
    }

    return answers
        .map((answer) => `<li class="${checkIsCorrect(answer)}">${answer.text}</li>`).join('')
}