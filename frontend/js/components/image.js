export function renderImage(type) {
    let image = ''
    if (type==='question') {
        image = `
            <img src="../../img/1640194547_50-abrakadabra-fun-p-dumayushchii-chelovechek-dlya-prezentatsii-64.png" alt="">
            <div class="to-quiz-list1">
                 <p class="p1">Пожалуй,</p>
                 <p class="p2">пройду</p>
                 <p class="p3">другой</p>
                 <p class="p4">квиз</p>
            </div>
        `
    }
    if (type==='result') {
        image = `
            <img src="../../img/Dollarphotoclub-45630939.jpg" alt="">
            <div class="to-quiz-list2">
                 <p class="p1">Я бы</p>
                 <p class="p2">прошел еще</p>
                 <p class="p3">один квиз</p>
            </div>
        `
    }
    return image
}