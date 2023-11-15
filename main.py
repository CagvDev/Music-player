import os, pygame, eyed3, io, random
from tkinter import Tk, filedialog, Button, Canvas, Listbox, Scrollbar, Scale, HORIZONTAL
from PIL import Image, ImageTk

playlist = list()
current_song = 0
playing = False

def initialize_mixer():
    if not pygame.mixer.get_init():
        pygame.mixer.init()

def load_songs():
    global current_song, playlist

    new_songs = filedialog.askopenfilenames(filetypes=[("MP3 files", "*.mp3")])

    if playlist and playing:
        playlist += list(new_songs)
        for new_song in new_songs:
            song_name = os.path.basename(new_song)
            listbox.insert("end", song_name)
    else:
        stop()

        playlist = list(new_songs)
        listbox.delete(0, "end")
        for song in playlist:
            song_name = os.path.basename(song)
            listbox.insert("end", song_name)

        if playlist:
            current_song = 0
            play()  # Ahora puedes llamar a play sin argumentos

def play():
    global current_song, playing, screen

    if playlist:
        initialize_mixer()

        pygame.mixer.music.load(playlist[current_song])
        pygame.mixer.music.play()

        playing = True

        # Verifica si la ventana principal existe antes de mostrar la portada del álbum
        if screen.winfo_exists():
            show_album_cover()

        pygame.mixer.music.set_endevent(pygame.USEREVENT)

        listbox.selection_clear(0, "end")
        listbox.selection_set(current_song)
        listbox.activate(current_song)
        listbox.itemconfig(current_song, {'bg': 'blue', 'fg': 'white'})

        check_music_status()

def stop():
    global playing, album_cover_photo
    if playing and pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    playing = False
    hide_album_cover()
    album_cover_photo = None

def show_album_cover():
    global album_cover_photo
    if playing:
        audiofile = eyed3.load(playlist[current_song])
        if audiofile.tag and audiofile.tag.images:
            image_data = audiofile.tag.images[0].image_data
            img = Image.open(io.BytesIO(image_data))

            img = img.resize((202, 202), resample=Image.LANCZOS)

            album_cover_photo = ImageTk.PhotoImage(img)

            canvas.create_image(0, 0, anchor="nw", image=album_cover_photo)
            canvas.album_cover_photo = album_cover_photo

def hide_album_cover():
    canvas.delete("all")

def check_music_status():
    global playing, screen

    if playing and pygame.get_init():
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                next_song()
                return

        if playing:
            screen.after(100, check_music_status)

def set_volume(value):
    initialize_mixer()  # Asegúrate de que el mezclador esté inicializado
    volume = float(value) / 100.0 
    pygame.mixer.music.set_volume(volume)

def next_song():
    global current_song
    stop()

    listbox.itemconfig(current_song, {'bg': 'white', 'fg': 'black'})

    current_song = (current_song + 1) % len(playlist)
    play()

def previous_song():
    global current_song
    stop()

    listbox.itemconfig(current_song, {'bg': 'white', 'fg': 'black'})

    current_song = (current_song - 1) % len(playlist)
    play()

def shuffle_songs():
    global playlist
    random.shuffle(playlist)
    listbox.delete(0, "end")
    for song in playlist:
        song_name = os.path.basename(song)
        listbox.insert("end", song_name)

screen = Tk()
screen.title("Music player")
screen.resizable(False, False)
screen.config(bg="#f7d4b7")

canvas = Canvas(screen, width=200, height=200, bg="#000000")
canvas.grid(row=1, column=0, rowspan=2)

listbox = Listbox(screen, selectmode="SINGLE", xscrollcommand=True, yscrollcommand=True)
listbox.grid(row=1, column=1, columnspan=4, sticky="nsew", pady=(0))

xscrollbar = Scrollbar(screen, orient=HORIZONTAL, command=listbox.xview)
xscrollbar.grid(row=2, column=1, columnspan=4, sticky="ew", pady=(0))
listbox.config(xscrollcommand=xscrollbar.set)

scrollbar = Scrollbar(screen, command=listbox.yview)
scrollbar.grid(row=1, column=5, sticky="nsew", padx=(0,5))
listbox.config(yscrollcommand=scrollbar.set)

load_button = Button(screen, text="Upload songs", command=lambda: load_songs(), bg="#75aac9", activebackground="#6193b0")
load_button.grid(row=0, column=1, pady=(10, 0), columnspan=3)

random_button = Button(screen, text="Random", command=shuffle_songs, bg="#de81ca", activebackground="#d177be")
random_button.grid(row=0, column=4, pady=(10, 0))

previous_button = Button(screen, text="Previous", command=previous_song, bg="#d6bd83", activebackground="#c9b075")
previous_button.grid(row=3, column=1, padx=5, pady=(0,5))

play_button = Button(screen, text="Play", command=play, bg="#22c77f", activebackground="#1bb572")
play_button.grid(row=3, column=2, padx=5, pady=(0, 5))

stop_button = Button(screen, text="Stop", command=stop, bg="#ba1c46", activebackground="#9c1337")
stop_button.grid(row=3, column=3, padx=5, pady=(0,5))

next_button = Button(screen, text="Next", command=next_song, bg="#d6bd83", activebackground="#c9b075")
next_button.grid(row=3, column=4, padx=5, pady=(0,5))
    
volume_slider = Scale(screen, from_=0, to=100, orient=HORIZONTAL, command=set_volume, showvalue=0)
volume_slider.set(50)
volume_slider.grid(row=3, column=0, padx=5, pady=(0,5))

screen.mainloop()