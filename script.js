function scrollChatToBottom() {
    var chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    var chatBox = document.getElementById('chat-box');

    chatBox.innerHTML += '<p><strong>Вы:</strong> ' + userInput + '</p>';

    axios.post('http://localhost:5005/webhooks/rest/webhook', {
        sender: 'user',
        message: userInput,
    }, {
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        var botResponse = response.data[0].text;
        chatBox.innerHTML += '<p><strong><Бот по посику аниме>:</strong> ' + botResponse + '</p>';

        if (response.data.length > 1) {
            chatBox.innerHTML += "<ul>";
            answers = response.data[1].text.split('\n');
            for (let i = 0; i < answers.length; i++) {
                chatBox.innerHTML += '<li>' + answers[i] + '</li>';
            }
            chatBox.innerHTML += "</ul>"
        }

        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => console.error('Ошибка:', error));

    document.getElementById('user-input').value = '';
}

document.getElementById('user-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Отменить стандартное поведение перехода на новую строку
        sendMessage();
    }
});
