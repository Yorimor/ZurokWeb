// search filters
const searchInput = document.querySelector('#search');
const noQuotes = document.querySelector("#noQuotes");
const qCount = document.querySelector("#qCount");

const userFilter = document.querySelector("#userFilter");
const userFilterMenu = document.querySelector("#userFilterMenu");

const rows = document.querySelectorAll("tbody>tr:not(#noQuotes)");
const quotes = [];
const users = [];
const removed = [];

for (let i = 0; i < rows.length; i++) {
    quotes.push(rows[i].children[1].innerText.toLowerCase());
    users.push(rows[i].children[3].innerText.toLowerCase());
}

let searchText = "";
let visibleNums = [];

searchInput.addEventListener("wa-input", () => { updateTable(); });
userFilter.addEventListener("wa-hide", () => { updateTable(); });

function updateTable() {
    searchText = searchInput.value.toLowerCase();

    visibleNums = [];
    for (let i = 0; i < userFilterMenu.childElementCount; i++)
    {
        if (userFilterMenu.children[i].checked) {
            visibleNums.push((i+1).toString());
        }
    }

    // console.log(visibleNums, searchText);

    let shown = 0;
    for (let i = 0; i < rows.length; i++) {
        if (visibleNums.includes(users[i]) && quotes[i].includes(searchText) && !removed.includes(i)) {
            rows[i].classList.remove("hidden");
            shown++;
        } else {
            rows[i].classList.add("hidden");
        }
    }
    isNoQuotes(shown);
}

function isNoQuotes(count) {
    if (count === 0) {
        noQuotes.classList.remove("hidden")
    } else {
        noQuotes.classList.add("hidden")
    }
    qCount.innerText = count;
}

isNoQuotes(rows.length);

// remove buttons
const removeBtns = document.querySelectorAll("td>wa-button");
// console.log(removeBtns);

for (let i = 0; i < removeBtns.length; i++) {
    removeBtns[i].addEventListener("click", async function () {
        console.log(removeBtns[i].parentElement.parentElement.id);
        removeBtns[i].loading = true;

        fetch("", {
              method: "POST",
              body: JSON.stringify({
                  "quote": removeBtns[i].parentElement.parentElement.id
              }),
              headers: {
                "Content-type": "application/json; charset=UTF-8"
              }
            })
            .then((response) => {
            if (response.status === 200) {
                removeBtns[i].parentElement.parentElement.classList.add("hidden");
                removed.push(i);
                updateTable();
            }
            else {
                console.log(response);
                alert_error(response.status + ": " + (response.text).toString());
            }
        })

        removeBtns[i].loading = false;
        removeBtns[i].disabled = true;
    });
}
