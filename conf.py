import pickle

variables = {
    "success_pic": "https://techbriefly.com/wp-content/uploads/2023/04/Best-blue-haired-anime-characters_04.jpg",
    "start_pic": "https://gas-kvas.com/uploads/posts/2023-01/1673414959_gas-kvas-com-p-mashet-rukoi-risunki-anime-31.jpg",
    "bye_pic": "https://i.pinimg.com/originals/d2/a5/fb/d2a5fb6fdebc3be6cc1c50041dc592e6.jpg",
}

with open("variables.pkl", "wb") as f:
    pickle.dump(variables, f)
