import flet as ft
from tinytag import TinyTag
from math import pi

index = 1  # index=0 pick_files_dialog
state = ""

tracks_list = [
    "sounds/outfoxing.mp3",
    "sounds/param_viper.mp3",
    "sounds/track_drums.mp3",
]
volume = 0.5


def main(page: ft.Page):
    page.title = "Music Player"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_height = 400
    page.window_width = 750
    page.window_min_width = 750
    page.window_min_height = 400

    # ************************      Functions          ******************************
    def pick_files_result(e: ft.FilePickerResultEvent):
        global tracks_list
        if e.files:
            for f in e.files:
                src = f.path.replace("\\", "/")
                tracks_list.append(src)
                audio1 = ft.Audio(
                    src=f"{src}",
                    autoplay=False,
                    volume=0.5,
                    balance=0,
                    on_position_changed=progress_change,
                    on_state_changed=check_state,
                )
                page.overlay.append(audio1)
            page.update()
        else:
            "Cancelled!"

    def check_state(e):
        global index
        if e.data == "completed":
            index = index + 1
            if index == len(page.overlay):
                index = 0
            new_track()
            btn_play.icon = ft.icons.PAUSE_CIRCLE
            page.update()

    def play_track(e):
        global index
        global state
        if state == "":
            state = "playing"
            btn_play.icon = ft.icons.PAUSE_CIRCLE
            page.overlay[index].play()
        elif state == "playing":
            state = "paused"
            btn_play.icon = ft.icons.PLAY_CIRCLE
            page.overlay[index].pause()
        else:  # if state=="paused"
            state = "playing"
            btn_play.icon = ft.icons.PAUSE_CIRCLE
            page.overlay[index].resume()
        page.update()

    def new_track():
        global index
        global state
        global volume
        disc_image.rotate.angle += pi * 2
        audio = TinyTag.get(page.overlay[index].src)
        track_name.value = audio.title
        track_artist.value = audio.artist
        current_time.value = "0:0"
        remaining_time.value = converter_time(audio.duration * 1000)
        progress_track.value = "0"
        if state == "playing":
            page.overlay[index].volume = volume
            page.overlay[index].play()

    def next_track(e):
        global index
        page.overlay[index].release()
        page.overlay[index].update()
        index = index + 1
        if index == len(page.overlay):
            index = 1
        new_track()
        page.update()

    def previous_track(e):
        global index
        page.overlay[index].release()
        page.overlay[index].update()
        index = index - 1
        if index == 0:
            index = len(page.overlay) - 1
        new_track()
        page.update()

    def volume_change(e):
        global index
        global volume
        v = e.control.value
        page.overlay[index].volume = 0.01 * v
        volume = 0.01 * v
        if v == 0:
            volume_icon.name = ft.icons.VOLUME_OFF
        elif 0 < v <= 50:
            volume_icon.name = ft.icons.VOLUME_DOWN
        elif 50 < v:
            volume_icon.name = ft.icons.VOLUME_UP
        page.update()

    def converter_time(millis):
        millis = int(millis)
        seconds = (millis / 1000) % 60
        seconds = int(seconds)
        minutes = (millis / (1000 * 60)) % 60
        minutes = int(minutes)
        return "%d:%d" % (minutes, seconds)

    def progress_change(e):
        global index
        audio = TinyTag.get(page.overlay[index].src)
        current_time.value = converter_time(e.data)
        remaining_time.value = converter_time((audio.duration * 1000) - int(e.data))
        progress_track.value = (float(e.data) * 1.0) / float(audio.duration * 1000)
        page.update()

    # *****************   Initializing player music values  **************
    # load pick_files_dialog
    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)
    # Load tracks to Page overlay
    for i in range(0, len(tracks_list)):
        audio1 = ft.Audio(
            # src=f"sounds/{tracks_list[i]}",
            src=f"{tracks_list[i]}",
            autoplay=False,
            volume=0.5,
            balance=0,
            on_position_changed=progress_change,
            on_state_changed=check_state,
        )
        page.overlay.append(audio1)

    audio_init = TinyTag.get(page.overlay[index].src)

    current_time = ft.Text(value="0:0")
    remaining_time = ft.Text(value=converter_time(audio_init.duration * 1000))
    progress_track = ft.ProgressBar(width=400, value="0", height=8)
    track_name = ft.Text(value=audio_init.title)
    track_artist = ft.Text(value=audio_init.artist)
    btn_play = ft.IconButton(
        icon=ft.icons.PLAY_CIRCLE, icon_size=50, on_click=play_track
    )
    volume_icon = ft.Icon(name=ft.icons.VOLUME_DOWN)

    disc_image = ft.Image(
        src=f"assets/album.png",
        width=180,
        height=180,
        fit=ft.ImageFit.CONTAIN,
        rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
        animate_rotation=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_CIRC),
    )
    main_content = ft.Card(
        content=ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=80, height=200),
                    ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.MUSIC_NOTE_ROUNDED),
                                title=track_name,
                                subtitle=track_artist,
                            ),
                            ft.Row(
                                [current_time, progress_track, remaining_time],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.SKIP_PREVIOUS,
                                        icon_size=40,
                                        on_click=previous_track,
                                    ),
                                    btn_play,
                                    ft.IconButton(
                                        icon=ft.icons.SKIP_NEXT,
                                        icon_size=40,
                                        on_click=next_track,
                                    ),
                                    volume_icon,
                                    ft.Slider(
                                        width=150,
                                        active_color=ft.colors.WHITE60,
                                        min=0,
                                        max=100,
                                        divisions=100,
                                        value=50,
                                        label="{value}",
                                        on_change=volume_change,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.PLAYLIST_ADD_ROUNDED,
                                        on_click=lambda _: pick_files_dialog.pick_files(
                                            allow_multiple=True,
                                            file_type=ft.FilePickerFileType.AUDIO,
                                        ),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ]
                    ),
                ]
            ),
        ),
        right=0,
        width=580,
        color=ft.colors.ON_PRIMARY,
        height=180,
    )

    stack = ft.Stack(
        controls=[
            main_content,
            disc_image,
        ],
        width=680,
        height=300,
    )

    page.add(stack)


ft.app(target=main)
