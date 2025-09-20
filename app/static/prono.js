function LowerScore(id) {
    const spanObject = document.getElementById(id);
    var homeScoreInt = parseInt(spanObject.innerText);
    if (homeScoreInt > 0) {
        homeScoreInt = homeScoreInt - 1;
        spanObject.innerText = homeScoreInt;
    }
}

function IncreaseScore(id) {
    const spanObject = document.getElementById(id);
    var homeScoreInt = parseInt(spanObject.innerText);
    homeScoreInt = homeScoreInt + 1;
    spanObject.innerText = homeScoreInt;
}

const IncHomeScore = document.getElementById("add-score-home");
const LowerHomeScore = document.getElementById("lower-score-home");
const IncAwayScore = document.getElementById("add-score-away");
const LowerAwayScore = document.getElementById("lower-score-away");

LowerHomeScore.addEventListener("click", () => {
    LowerScore("home-score");
})

LowerAwayScore.addEventListener("click", () => {
    LowerScore("away-score");
})

IncHomeScore.addEventListener("click", () => {
    IncreaseScore("home-score");
});

IncAwayScore.addEventListener("click", () => {
    IncreaseScore("away-score");
});

document.getElementById("update-pronostiek").addEventListener("click", function() {
    const homeScore = parseInt(document.getElementById("home-score").innerText);
    const awayScore = parseInt(document.getElementById("away-score").innerText);
    const pronoId = parseInt(document.getElementById("hidden_id").innerText);

    fetch(`/update_prono/${pronoId}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            home_score: homeScore,
            away_score: awayScore
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = "/matches";
        }
    });
});
