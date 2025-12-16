# ipc_project/gui/dashboard.py

import tkinter as tk
from tkinter import ttk

from gui.theme import apply_dark_theme
from gui.widgets.log_panel import LogPanel
from core.process_manager import ProcessManager
from core.ipc_manager import IPCManager
from core.security import SecurityManager
from core.utils.logger import AppLogger


class ControlRoomApp(tk.Tk):
    """
    Main Tkinter application – the IPC Control Room.
    """

    def __init__(
        self,
        process_manager: ProcessManager,
        ipc_manager: IPCManager,
        security_manager: SecurityManager,
        logger: AppLogger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.process_manager = process_manager
        self.ipc_manager = ipc_manager
        self.security_manager = security_manager
        self.logger = logger

        self.title("IPC Control Room – Inter-Process Communication Framework")
        self.geometry("1200x700")
        self.minsize(960, 600)

        apply_dark_theme(self)

        # Layout: top bar, center pane (left processes + right tabs), bottom log
        self._create_widgets()

        # Connect logger to log panel
        self.logger.register_sink(self.log_panel.append_entry)

        # Initial log entry
        self.logger.info("Control Room initialized.")

    def _create_widgets(self) -> None:
        # Top bar
        top_frame = ttk.Frame(self, style="Panel.TFrame")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ttk.Label(
            top_frame,
            text="IPC Control Room",
            style="Header.TLabel",
        )
        title_label.pack(side=tk.LEFT, padx=12, pady=8)

        # Process control buttons
        btn_add_proc = ttk.Button(
            top_frame,
            text="Create Test Process",
            command=self._on_create_test_process,
        )
        btn_add_proc.pack(side=tk.RIGHT, padx=8, pady=8)

        btn_kill_proc = ttk.Button(
            top_frame,
            text="Terminate Selected",
            command=self._on_terminate_selected,
        )
        btn_kill_proc.pack(side=tk.RIGHT, padx=8, pady=8)

        # Central paned window: left = process list, right = tabs
        center_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        center_paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left panel: process list
        self.process_frame = ttk.Frame(center_paned, style="Panel.TFrame")
        center_paned.add(self.process_frame, weight=1)

        self._create_process_panel(self.process_frame)

        # Right panel: notebook tabs
        self.tabs_frame = ttk.Frame(center_paned, style="Panel.TFrame")
        center_paned.add(self.tabs_frame, weight=3)

        self._create_tabs(self.tabs_frame)
       
        self._refresh_pipe_process_menus()
        self._refresh_queue_process_menus()
        self._refresh_shm_process_menus()




        # Bottom log panel
        self.log_panel = LogPanel(self)
        self.log_panel.pack(side=tk.BOTTOM, fill=tk.X)

    # ----- Process panel -----

    def _create_process_panel(self, parent: ttk.Frame) -> None:
        header = ttk.Label(parent, text="Processes", style="Header.TLabel")
        header.pack(side=tk.TOP, anchor="w", padx=8, pady=(8, 4))

        self.process_listbox = tk.Listbox(
            parent,
            height=15,
            activestyle="none",
            bg="#151515",
            fg="#f0f0f0",
            selectbackground="#3aa8ff",
            selectforeground="#000000",
            borderwidth=0,
            highlightthickness=0,
        )
        self.process_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Simple placeholder – in future connect to real processes
        ttk.Label(
            parent,
            text="(Test processes will appear here)",
        ).pack(side=tk.TOP, anchor="w", padx=8, pady=(4, 8))

    # ----- Tabs -----

    def _create_tabs(self, parent: ttk.Frame) -> None:
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Pipes tab
        pipes_tab = ttk.Frame(notebook, style="Panel.TFrame")
        notebook.add(pipes_tab, text="Pipes")
        self._build_pipes_tab(pipes_tab)

        # Queue tab
        queue_tab = ttk.Frame(notebook, style="Panel.TFrame")
        notebook.add(queue_tab, text="Message Queues")
        self._build_queue_tab(queue_tab)

        # Shared memory tab
        shm_tab = ttk.Frame(notebook, style="Panel.TFrame")
        notebook.add(shm_tab, text="Shared Memory")
        self._build_shm_tab(shm_tab)

        # Test programs tab
        test_tab = ttk.Frame(notebook, style="Panel.TFrame")
        notebook.add(test_tab, text="Test Programs")
        self._build_test_tab(test_tab)

        # Chaos mode tab
        chaos_tab = ttk.Frame(notebook, style="Panel.TFrame")
        notebook.add(chaos_tab, text="Chaos Mode")
        self._build_chaos_tab(chaos_tab)

    def _build_pipes_tab(self, parent: ttk.Frame) -> None:
        """
        Build a minimal working UI for pipes:
        - Sender dropdown
        - Receiver dropdown
        - Create Pipe
        - Send message
        - Receive message
        """

        # ---- Section Header ----
        header = ttk.Label(parent, text="Pipe Communication", style="Header.TLabel")
        header.pack(anchor="w", padx=10, pady=(10, 6))

        top_frame = ttk.Frame(parent, style="Panel.TFrame")
        top_frame.pack(fill=tk.X, padx=10)

        # ---- Sender Dropdown ----
        ttk.Label(top_frame, text="Sender Process:").grid(row=0, column=0, sticky="w")
        self.pipe_sender_var = tk.StringVar()
        self.pipe_sender_menu = ttk.Combobox(top_frame, textvariable=self.pipe_sender_var)
        self.pipe_sender_menu.grid(row=0, column=1, padx=6, pady=4)

        # ---- Receiver Dropdown ----
        ttk.Label(top_frame, text="Receiver Process:").grid(row=1, column=0, sticky="w")
        self.pipe_receiver_var = tk.StringVar()
        self.pipe_receiver_menu = ttk.Combobox(top_frame, textvariable=self.pipe_receiver_var)
        self.pipe_receiver_menu.grid(row=1, column=1, padx=6, pady=4)

        # ---- Create Channel Button ----
        self.btn_create_pipe = ttk.Button(
            top_frame,
            text="Create Pipe Channel",
            command=self._on_create_pipe_channel
        )
        self.btn_create_pipe.grid(row=2, column=0, columnspan=2, pady=(8, 12))

        # Store created pipe reference
        self.current_pipe_channel = None

        # ---- Separator ----
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=6)

        # ---- Send/Receive Section ----
        msg_frame = ttk.Frame(parent, style="Panel.TFrame")
        msg_frame.pack(fill=tk.X, padx=10)

        ttk.Label(msg_frame, text="Message:").grid(row=0, column=0, sticky="w")
        self.pipe_message_var = tk.StringVar()
        self.pipe_message_entry = ttk.Entry(msg_frame, textvariable=self.pipe_message_var, width=40)
        self.pipe_message_entry.grid(row=0, column=1, padx=6, pady=4)

        btn_send = ttk.Button(
            msg_frame,
            text="Send Message",
            command=self._on_pipe_send,
        )
        btn_send.grid(row=1, column=0, columnspan=2, pady=(4, 8))

        btn_receive = ttk.Button(
            msg_frame,
            text="Receive Message",
            command=self._on_pipe_receive,
        )
        btn_receive.grid(row=2, column=0, columnspan=2, pady=(4, 8))
        # Animation canvas
        self.pipe_canvas = tk.Canvas(parent, height=40, bg="#000000", highlightthickness=0)
        self.pipe_canvas.pack(fill=tk.X, padx=10, pady=10)


        # Received messages viewer
        self.pipe_output = tk.Text(
            parent,
            height=8,
            bg="#101010",
            fg="#f0f0f0",
            borderwidth=0,
            highlightthickness=0,
        )
        self.pipe_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def _build_queue_tab(self, parent: ttk.Frame) -> None:
        """
        Basic UI for message queues:
        - Sender dropdown
        - Receiver dropdown
        - Create Queue Channel
        - Enqueue / Dequeue
        """
        header = ttk.Label(parent, text="Message Queue Communication", style="Header.TLabel")
        header.pack(anchor="w", padx=10, pady=(10, 6))

        top_frame = ttk.Frame(parent, style="Panel.TFrame")
        top_frame.pack(fill=tk.X, padx=10)

        # Sender
        ttk.Label(top_frame, text="Sender Process:").grid(row=0, column=0, sticky="w")
        self.queue_sender_var = tk.StringVar()
        self.queue_sender_menu = ttk.Combobox(top_frame, textvariable=self.queue_sender_var)
        self.queue_sender_menu.grid(row=0, column=1, padx=6, pady=4)

        # Receiver
        ttk.Label(top_frame, text="Receiver Process:").grid(row=1, column=0, sticky="w")
        self.queue_receiver_var = tk.StringVar()
        self.queue_receiver_menu = ttk.Combobox(top_frame, textvariable=self.queue_receiver_var)
        self.queue_receiver_menu.grid(row=1, column=1, padx=6, pady=4)

        # Create queue channel
        self.btn_create_queue = ttk.Button(
            top_frame,
            text="Create Queue Channel",
            command=self._on_create_queue_channel,
        )
        self.btn_create_queue.grid(row=2, column=0, columnspan=2, pady=(8, 12))

        self.current_queue_channel = None

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=6)

        # Message section
        msg_frame = ttk.Frame(parent, style="Panel.TFrame")
        msg_frame.pack(fill=tk.X, padx=10)

        ttk.Label(msg_frame, text="Message:").grid(row=0, column=0, sticky="w")
        self.queue_message_var = tk.StringVar()
        self.queue_message_entry = ttk.Entry(msg_frame, textvariable=self.queue_message_var, width=40)
        self.queue_message_entry.grid(row=0, column=1, padx=6, pady=4)

        btn_send = ttk.Button(
            msg_frame,
            text="Enqueue Message",
            command=self._on_queue_send,
        )
        btn_send.grid(row=1, column=0, columnspan=2, pady=(4, 8))

        btn_receive = ttk.Button(
            msg_frame,
            text="Dequeue Message",
            command=self._on_queue_receive,
        )
        btn_receive.grid(row=2, column=0, columnspan=2, pady=(4, 8))

        # Output viewer
        self.queue_output = tk.Text(
            parent,
            height=8,
            bg="#101010",
            fg="#f0f0f0",
            borderwidth=0,
            highlightthickness=0,
        )
        self.queue_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    ###########################################################

    def _build_shm_tab(self, parent: ttk.Frame) -> None:
        """
        UI for Shared Memory:
        - Writer and Reader dropdowns
        - Create SHM channel
        - Write / Read operations
        - Visual display of current value
        """
        header = ttk.Label(parent, text="Shared Memory Channel", style="Header.TLabel")
        header.pack(anchor="w", padx=10, pady=(10, 6))

        top_frame = ttk.Frame(parent, style="Panel.TFrame")
        top_frame.pack(fill=tk.X, padx=10)

        # Writer
        ttk.Label(top_frame, text="Writer Process:").grid(row=0, column=0, sticky="w")
        self.shm_writer_var = tk.StringVar()
        self.shm_writer_menu = ttk.Combobox(top_frame, textvariable=self.shm_writer_var)
        self.shm_writer_menu.grid(row=0, column=1, padx=6, pady=4)

        # Reader
        ttk.Label(top_frame, text="Reader Process:").grid(row=1, column=0, sticky="w")
        self.shm_reader_var = tk.StringVar()
        self.shm_reader_menu = ttk.Combobox(top_frame, textvariable=self.shm_reader_var)
        self.shm_reader_menu.grid(row=1, column=1, padx=6, pady=4)

        # Create SHM channel
        self.btn_create_shm = ttk.Button(
            top_frame,
            text="Create Shared Memory Segment",
            command=self._on_create_shm_channel,
        )
        self.btn_create_shm.grid(row=2, column=0, columnspan=2, pady=(8, 12))

        self.current_shm_channel = None

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=6)

        # Write/Read section
        mid_frame = ttk.Frame(parent, style="Panel.TFrame")
        mid_frame.pack(fill=tk.X, padx=10)

        ttk.Label(mid_frame, text="Value to Write:").grid(row=0, column=0, sticky="w")
        self.shm_value_var = tk.StringVar()
        self.shm_value_entry = ttk.Entry(mid_frame, textvariable=self.shm_value_var, width=40)
        self.shm_value_entry.grid(row=0, column=1, padx=6, pady=4)

        btn_write = ttk.Button(
            mid_frame,
            text="Write to Shared Memory",
            command=self._on_shm_write,
        )
        btn_write.grid(row=1, column=0, columnspan=2, pady=(4, 8))

        btn_read = ttk.Button(
            mid_frame,
            text="Read from Shared Memory",
            command=self._on_shm_read,
        )
        btn_read.grid(row=2, column=0, columnspan=2, pady=(4, 8))

        # Visual display of current SHM contents
        visual_frame = ttk.Frame(parent, style="Panel.TFrame")
        visual_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(visual_frame, text="Shared Memory Contents:").pack(anchor="w", pady=(0, 4))

        self.shm_display = tk.Text(
            visual_frame,
            height=6,
            bg="#101010",
            fg="#f0f0f0",
            borderwidth=0,
            highlightthickness=0,
            state="disabled",
            wrap="word",
        )
        self.shm_display.pack(fill=tk.BOTH, expand=True)

    ###########################################################
    def _build_test_tab(self, parent):
        header = ttk.Label(parent, text="Test Processes", style="Header.TLabel")
        header.pack(anchor="w", padx=10, pady=(10, 6))

        btn_ping = ttk.Button(
            parent,
            text="Start Ping Process (Pipe)",
            command=self._start_ping_test,
        )
        btn_ping.pack(padx=10, pady=6, anchor="w")

        btn_echo = ttk.Button(
            parent,
            text="Start Echo Process (Pipe)",
            command=self._start_echo_test,
        )
        btn_echo.pack(padx=10, pady=6, anchor="w")

        ttk.Label(parent, text="NOTE: Use pipe sender/receiver dropdowns first.").pack(anchor="w", padx=10, pady=4)







    def _build_chaos_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Chaos Mode Controller (placeholder)").pack(
            padx=10, pady=10, anchor="w"
        )

    # ----- Top bar callbacks -----

    def _on_create_test_process(self) -> None:
        """
        Placeholder handler for creating a test process.
        Later, this will open a small dialog to choose type and name.
        """
        

        proc_info = self.process_manager.create_dummy_process()
        
        display_name = f"{proc_info['id']} – {proc_info['name']} ({proc_info['role']})"
        self.process_listbox.insert(tk.END, display_name)
        self.logger.info(f"Created test process: {display_name}")

       
        self._refresh_pipe_process_menus()
        self._refresh_queue_process_menus()
        self._refresh_shm_process_menus()


    def _on_terminate_selected(self) -> None:
        selection = self.process_listbox.curselection()
        if not selection:
            self.logger.warning("Terminate requested, but no process selected.")
            return

        index = selection[0]
        item_text = self.process_listbox.get(index)
        self.process_listbox.delete(index)

        # In a later revision, parse the ID and signal the manager
        self.logger.info(f"Terminated process (UI only for now): {item_text}")
    def _refresh_pipe_process_menus(self) -> None:
        processes = self.process_manager.list_processes()
        labels = [f"{p.id}:{p.name}" for p in processes]
        self.pipe_sender_menu["values"] = labels
        self.pipe_receiver_menu["values"] = labels


    def _refresh_queue_process_menus(self) -> None:
        processes = self.process_manager.list_processes()
        labels = [f"{p.id}:{p.name}" for p in processes]

        if hasattr(self, "queue_sender_menu"):
            self.queue_sender_menu["values"] = labels
        if hasattr(self, "queue_receiver_menu"):
            self.queue_receiver_menu["values"] = labels


    def _refresh_shm_process_menus(self) -> None:
        """
        Refresh writer and reader dropdowns for the SHM tab.
        """
        processes = self.process_manager.list_processes()
        labels = [f"{p.id}:{p.name}" for p in processes]

        if hasattr(self, "shm_writer_menu"):
            self.shm_writer_menu["values"] = labels
        if hasattr(self, "shm_reader_menu"):
            self.shm_reader_menu["values"] = labels

    
    def _on_create_pipe_channel(self) -> None:
        
        sender_label = self.pipe_sender_var.get()
        receiver_label = self.pipe_receiver_var.get()

        if not sender_label or not receiver_label:
            self.logger.warning("Both sender and receiver must be selected to create a pipe.")
            return

        # Extract numeric IDs
        sender_id = int(sender_label.split(":")[0])
        receiver_id = int(receiver_label.split(":")[0])

        # Create pipe channel
        self.current_pipe_channel = self.ipc_manager.create_pipe_channel(
            name=f"pipe_{sender_id}_to_{receiver_id}",
            allowed_senders=[sender_id],
            allowed_receivers=[receiver_id],
        )

        self.logger.info(
            f"Pipe channel created: sender={sender_id}, receiver={receiver_id}"
        )
    def _on_pipe_send(self) -> None:
        if not self.current_pipe_channel:
            self.logger.warning("No pipe channel created yet.")
            return

        msg = self.pipe_message_var.get().strip()
        if not msg:
            self.logger.warning("Cannot send empty message.")
            return

        # Extract sender ID
        s_label = self.pipe_sender_var.get()
        if not s_label:
            self.logger.warning("Select a sender before sending.")
            return
        sender_id = int(s_label.split(":")[0])

        self.current_pipe_channel.send_message(sender_id=sender_id, payload=msg)
        self._animate_pipe_dot()
    def _on_pipe_receive(self) -> None:
        if not self.current_pipe_channel:
            self.logger.warning("No pipe channel created.")
            return

        # Extract receiver ID
        r_label = self.pipe_receiver_var.get()
        if not r_label:
            self.logger.warning("Select a receiver before receiving.")
            return
        receiver_id = int(r_label.split(":")[0])

        msg = self.current_pipe_channel.receive_message(receiver_id=receiver_id, block=False)
        if msg is None:
            self.logger.info("No message available to receive.")
            return

        # Display to text panel
        self.pipe_output.insert(tk.END, f"Received: {msg}\n")
        self.pipe_output.see(tk.END)
    def _on_pipe_receive(self) -> None:
        if not self.current_pipe_channel:
            self.logger.warning("No pipe channel created.")
            return

        # Extract receiver ID
        r_label = self.pipe_receiver_var.get()
        if not r_label:
            self.logger.warning("Select a receiver before receiving.")
            return
        receiver_id = int(r_label.split(":")[0])

        msg = self.current_pipe_channel.receive_message(receiver_id=receiver_id, block=False)
        if msg is None:
            self.logger.info("No message available to receive.")
            return

        # Display to text panel
        self.pipe_output.insert(tk.END, f"Received: {msg}\n")
        self.pipe_output.see(tk.END)
    def _on_create_queue_channel(self) -> None:
        sender_label = self.queue_sender_var.get()
        receiver_label = self.queue_receiver_var.get()

        if not sender_label or not receiver_label:
            self.logger.warning("Both sender and receiver must be selected to create a queue.")
            return

        sender_id = int(sender_label.split(":")[0])
        receiver_id = int(receiver_label.split(":")[0])

        # For queues, it's fine if sender == receiver, but we can allow it.
        self.current_queue_channel = self.ipc_manager.create_queue_channel(
            name=f"queue_{sender_id}_to_{receiver_id}",
            allowed_senders=[sender_id],
            allowed_receivers=[receiver_id],
        )

        self.logger.info(
            f"Queue channel created: sender={sender_id}, receiver={receiver_id}"
        )


    def _on_queue_send(self) -> None:
        if not self.current_queue_channel:
            self.logger.warning("No queue channel created yet.")
            return

        msg = self.queue_message_var.get().strip()
        if not msg:
            self.logger.warning("Cannot enqueue empty message.")
            return

        s_label = self.queue_sender_var.get()
        if not s_label:
            self.logger.warning("Select a sender before enqueueing.")
            return
        sender_id = int(s_label.split(":")[0])

        self.current_queue_channel.send_message(sender_id=sender_id, payload=msg)


    def _on_queue_receive(self) -> None:
        if not self.current_queue_channel:
            self.logger.warning("No queue channel created.")
            return

        r_label = self.queue_receiver_var.get()
        if not r_label:
            self.logger.warning("Select a receiver before dequeuing.")
            return
        receiver_id = int(r_label.split(":")[0])

        msg = self.current_queue_channel.receive_message(receiver_id=receiver_id, block=False)
        if msg is None:
            self.logger.info("No message available in queue.")
            return

        self.queue_output.insert(tk.END, f"Dequeued: {msg}\n")
        self.queue_output.see(tk.END)


    def _on_create_shm_channel(self) -> None:
        writer_label = self.shm_writer_var.get()
        reader_label = self.shm_reader_var.get()

        if not writer_label or not reader_label:
            self.logger.warning("Writer and Reader must be selected to create shared memory.")
            return

        writer_id = int(writer_label.split(":")[0])
        reader_id = int(reader_label.split(":")[0])

        # It's perfectly fine for writer and reader to be the same in SHM,
        # but your demo is nicer when they differ.
        self.current_shm_channel = self.ipc_manager.create_shared_memory_channel(
            name=f"shm_{writer_id}_to_{reader_id}",
            allowed_senders=[writer_id],
            allowed_receivers=[reader_id],
            buffer_size=256,
        )

        self.logger.info(
            f"Shared memory channel created: writer={writer_id}, reader={reader_id}"
        )


    def _on_shm_write(self) -> None:
        if not self.current_shm_channel:
            self.logger.warning("No shared memory channel created yet.")
            return

        value = self.shm_value_var.get()
        if value is None:
            value = ""
        value = value.strip()

        writer_label = self.shm_writer_var.get()
        if not writer_label:
            self.logger.warning("Select a writer before writing to shared memory.")
            return

        writer_id = int(writer_label.split(":")[0])

        ok = self.current_shm_channel.write_value(sender_id=writer_id, text=value)
        if ok:
            self._update_shm_display(f"WROTE: {value}")


    def _on_shm_read(self) -> None:
        if not self.current_shm_channel:
            self.logger.warning("No shared memory channel created.")
            return

        reader_label = self.shm_reader_var.get()
        if not reader_label:
            self.logger.warning("Select a reader before reading shared memory.")
            return

        reader_id = int(reader_label.split(":")[0])

        value = self.current_shm_channel.read_value(receiver_id=reader_id)
        if value is None:
            self.logger.info("Shared memory read returned None.")
            return

        self._update_shm_display(f"READ: {value}")
    def _update_shm_display(self, line: str) -> None:
        """
        Append a line to the shared memory display box.
        """
        self.shm_display.configure(state="normal")
        self.shm_display.insert(tk.END, line + "\n")
        self.shm_display.see(tk.END)
        self.shm_display.configure(state="disabled")

    def _animate_pipe_dot(self):
        self.pipe_canvas.delete("all")
        r = 8
        dot = self.pipe_canvas.create_oval(0, 20-r, 2*r, 20+r, fill="#3aa8ff", outline="")

        def move():
            x = self.pipe_canvas.coords(dot)[2]  # right side of the circle
            if x < self.pipe_canvas.winfo_width():
                self.pipe_canvas.move(dot, 5, 0)
                self.pipe_canvas.after(10, move)
            else:
                self.pipe_canvas.delete(dot)

        move()

    def _start_ping_test(self):
        if not self.current_pipe_channel:
            self.logger.warning("Create a pipe channel first before starting a Ping process.")
            return

        sender_label = self.pipe_sender_var.get()
        if not sender_label:
            self.logger.warning("Select a sender process for Ping worker.")
            return

        sender_id = int(sender_label.split(":")[0])

        proc_id, worker, out_q = self.process_manager.create_ping_process(
            self.current_pipe_channel, sender_id
        )

        # Display process in the left panel
        self.process_listbox.insert(tk.END, f"{proc_id} – PingWorker")

    def _start_echo_test(self):
        if not self.current_pipe_channel:
            self.logger.warning("Create a pipe channel first before starting an Echo process.")
            return

        sender_label = self.pipe_sender_var.get()
        receiver_label = self.pipe_receiver_var.get()

        if not sender_label or not receiver_label:
            self.logger.warning("Select sender and receiver before starting Echo worker.")
            return

        receiver_id = int(receiver_label.split(":")[0])
        sender_id = int(sender_label.split(":")[0])

        proc_id, worker, out_q = self.process_manager.create_echo_process(
            self.current_pipe_channel, receiver_id, sender_id
        )

        self.process_listbox.insert(tk.END, f"{proc_id} – EchoWorker")

