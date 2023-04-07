export function getContactForm(quiz) {
    $(function () {
        $("#phone").mask("+375(99) 999-99-99");
        $("#email").inputmask("email");
    });

    return `
        <form class="form-data" id="form-data">` +
        (quiz.is_send_name ? '<input class="form-control" id="name" name="name" placeholder="Введите имя">' : '') +
        (quiz.is_send_email ? '<input class="form-control" id="email" name="email" placeholder="Введите email">' : '') +
        (quiz.is_send_phone ? '<input class="form-control" id="phone" name="phone" placeholder="Введите телефон">' : '') +
        `<button type="submit" class="btn btn-success">Отправить результаты</button> 
        </form> `
}