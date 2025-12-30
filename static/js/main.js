// 글자 수 카운터
const textarea = document.getElementById('content');
const charCount = document.getElementById('charCount');

textarea.addEventListener('input', () => {
    charCount.textContent = textarea.value.length;
});

// 폼 제출
const form = document.getElementById('letterForm');
const submitBtn = form.querySelector('.submit-btn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // 버튼 비활성화
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').textContent = '전송 중...';

    const formData = {
        recipient_email: document.getElementById('email').value,
        content: document.getElementById('content').value
    };

    try {
        const response = await fetch('/letters/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showSuccessModal();
            form.reset();
            charCount.textContent = '0';
        } else {
            const error = await response.json();
            showErrorModal(error.detail || '편지 전송에 실패했습니다.');
        }
    } catch (error) {
        showErrorModal('서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.');
    } finally {
        // 버튼 다시 활성화
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').textContent = '편지 보내기';
    }
});

// 성공 모달 표시
function showSuccessModal() {
    const modal = document.getElementById('successModal');
    modal.classList.add('show');
}

// 성공 모달 닫기
function closeModal() {
    const modal = document.getElementById('successModal');
    modal.classList.remove('show');
}

// 에러 모달 표시
function showErrorModal(message) {
    const modal = document.getElementById('errorModal');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    modal.classList.add('show');
}

// 에러 모달 닫기
function closeErrorModal() {
    const modal = document.getElementById('errorModal');
    modal.classList.remove('show');
}

// 모달 외부 클릭시 닫기
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
});
