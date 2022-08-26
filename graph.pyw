import pygame
import tkinter
from tkinter import ttk
from tkinter import filedialog
import sys
import pickle
import time

default_color = (255, 255, 255)
line_color = (0, 0, 0)
png_desc = "Portable Network Graphic file (PNG)"
jpg_desc = "JPEG file"
vision_types = ("None", "Distant", "Scouted", "Mapped", "Occupied")

class Screen:
	def __init__(self, map, pixel_size = 20):
		self._map = map
		self._screen_width = map._width * pixel_size
		self._screen_height = map._height * pixel_size
		self._pixel_width = map._width
		self._pixel_height = map._height
		self._pixel_size = pixel_size
		self._token_storage = TokenStorage()
		self._lines = True
		self._fog_enabled = False
		self._select_highlight = True
		self._show_notes = False
		self._show_tokens = True
		self._double_width_lines = True
		self._show_vision = True
		
	def init_pygame(self):
		self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))
		pygame.display.set_caption("Map Maker")
		self._screen.fill(default_color)
		pygame.display.flip()
		
	def draw_pygame(self):
		self._screen.fill(default_color)
		for y_pixel in range(0, self._map._height):
			for x_pixel in range(0, self._map._width):
				self._map.get_at(x_pixel, y_pixel).draw(self._screen, x_pixel*self._pixel_size, y_pixel*self._pixel_size, self._pixel_size, 
														self._select_highlight, self._show_notes, self._show_vision, self._double_width_lines)
		
		if self._show_tokens:
			self._token_storage.draw(self._screen, self._pixel_size)
		
		if self._fog_enabled:
			for y_pixel in range(0, map._height):
				for x_pixel in range(0, map._width):
					self._map.get_at(x_pixel, y_pixel).draw_fog(self._screen, x_pixel*self._pixel_size, y_pixel*self._pixel_size, self._pixel_size,
																self._select_highlight, self._double_width_lines)
		
		if self._lines:
			self.draw_lines()
				
	def draw_lines(self):
		for x_pixel in range(0, self._pixel_width):
			x = ((x_pixel+1) * self._pixel_size)-1
			pygame.draw.line(self._screen, line_color, (x, 0), (x, self._screen_height))
		for y_pixel in range(0, self._pixel_height):
			y = ((y_pixel+1) * self._pixel_size)-1
			pygame.draw.line(self._screen, line_color, (0, y), (self._screen_width, y))
		if self._double_width_lines:
			for x_pixel in range(0, self._pixel_width):
				x = (x_pixel * self._pixel_size)
				pygame.draw.line(self._screen, line_color, (x, 0), (x, self._screen_height))
			for y_pixel in range(0, self._pixel_height):
				y = (y_pixel * self._pixel_size)
				pygame.draw.line(self._screen, line_color, (0, y), (self._screen_width, y))
				
	def export_display(self):
		pygame.image.save(self._screen, time.strftime("./Screenshots/%m-%d-%y - %H-%M-%S.png"))
				
		
class Map:
	def __init__(self, width, height):
		self._width = width
		self._height = height
		self._data = [[MapNode() for x in range(0, self._width)] for y in range(0, self._height)]
		
	def fix_from_load(self, template_storage):
		for row in self._data:
			for node in row:
				node.fix_from_load(template_storage)
				
	def prepare_for_save(self, template_storage):
		for row in self._data:
			for node in row:
				node.prepare_for_save(template_storage)
		
	def apply_base_descriptor(self, base_descriptor):
		n = [[node for node in row if node._descriptor == None] for row in self._data]
		for row in n:
			for node in row:
				node._descriptor = base_descriptor
				
	def get_at(self, x, y):
		return self._data[y][x]
		
class MapNode:
	def __init__(self):
		self._descriptor = None
		self._selected = False
		self._notes = "\n"
		self._fog_of_war = True
		self._vision_type = "None"
		
	def fix_from_load(self, template_storage):
		if isinstance(self._descriptor, str):
			self._descriptor = template_storage.data[self._descriptor]
			
		if not hasattr(self, "_notes"):
			self._notes = "\n"
			
		if not hasattr(self, "_fog_of_war"):
			self._fog_of_war = True
			
		if not hasattr(self, "_vision_type"):
			self._vision_type = "None"
			
		self._selected = False
			
	def prepare_for_save(self, template_storage):
		self._descriptor = [key for key in template_storage.data if template_storage.data[key] == self._descriptor][0]
		self._selected = False
		
	def draw(self, pygame_display, xcorner, ycorner, pixel_size, show_selected, show_notes, show_vision, double_lined):
		if self._descriptor != None:
			self._descriptor.draw(pygame_display, xcorner, ycorner, pixel_size)	
		if show_notes:
			self.draw_corner_note(pygame_display, xcorner, ycorner, pixel_size)
		if show_vision:
			self.draw_vision_indicator(pygame_display, xcorner, ycorner, pixel_size)
		if self._selected and show_selected:
			self.draw_selection_box(pygame_display, xcorner, ycorner, pixel_size, double_lined)
		
	def draw_fog(self, pygame_display, xcorner, ycorner, pixel_size, show_selected, double_lined):
		if self._fog_of_war:
			self.draw_fog_of_war(pygame_display, xcorner, ycorner, pixel_size)
			if self._selected and show_selected:
				self.draw_selection_box(pygame_display, xcorner, ycorner, pixel_size, double_lined)
		
	def draw_selection_box(self, pygame_display, xcorner, ycorner, pixel_size, double_lined):
		i = 0
		if double_lined:
			i = 1
		rect = (xcorner+i, ycorner+i, pixel_size-2-i, pixel_size-2-i)
		pygame.draw.rect(pygame_display, (191, 191, 0), rect, 2)
		
	def draw_fog_of_war(self, pygame_display, xcorner, ycorner, pixel_size):
		rect = (xcorner, ycorner, pixel_size, pixel_size)
		pygame_display.fill((170, 170, 170), rect)
		iter = False
		for y in range (ycorner, ycorner+pixel_size):
			for x in range(xcorner, xcorner+pixel_size):
				if iter:
					pygame_display.set_at((x, y), (120, 120, 120))
				iter = not iter
			if pixel_size % 2 != 1:
				iter = not iter
				
	def draw_corner_note(self, pygame_display, xcorner, ycorner, pixel_size):
		if self._notes.strip() != "":
			#should never happen but here anyways
			if pixel_size < 6:
				return
			corners = ((xcorner+pixel_size, ycorner), (xcorner+pixel_size, ycorner+5), (xcorner+pixel_size-5, ycorner))
			pygame.draw.polygon(pygame_display, (0, 0, 0), corners)
			
	def draw_vision_indicator(self, pygame_display, xcorner, ycorner, pixel_size):
		if self._vision_type == "None":
			return
		color = None
		if self._vision_type == "Distant":
			color = (255, 0, 0)
		elif self._vision_type == "Mapped":
			color = (255, 53, 184)
		elif self._vision_type == "Scouted":
			color = (0, 255, 0)
		elif self._vision_type == "Occupied":
			color = (0, 0, 255)
		nx = xcorner+pixel_size-1
		ny = ycorner+pixel_size-1
			
		pygame.draw.lines(pygame_display, color, True, ((xcorner, ycorner), (xcorner, ny), (nx, ny), (nx, ycorner)))
	
class NodeDescriptor:
	def __init__(self, rgb, image):
		self.red = rgb[0]
		self.green = rgb[1]
		self.blue = rgb[2]
		self._image = image
		
	def draw(self, pygame_display, xcorner, ycorner, pixel_size):
		rect = (xcorner, ycorner, pixel_size, pixel_size)
		pygame_display.fill((self.red, self.green, self.blue), rect)
		if self._image != None:
			pygame_display.blit(picture, (xcorner,ycorner))
	
class TemplateStorage:
	def __init__(self):
		self.data = {"unnamed" : NodeDescriptor((255, 255, 255), None)}
		self.current = "unnamed"
		
	def make_new(self):
		if "unnamed" not in self.data:
			self.data["unnamed"] = NodeDescriptor((255, 255, 255), None)
			self.current = "unnamed"
		else:
			next = 1
			name = "unnamed (" + str(next) + ")"
			while name in self.data:
				next += 1
				name = "unnamed (" + str(next) + ")"
			self.data[name] = NodeDescriptor((0, 255, 255), None)
			self.current = name
			
	#get current
	def get_c(self):
		return self.data[self.current]
	
class TokenStorage:
	def __init__(self):
		self.data = {"unnamed": TokenDescriptor()}
		
	def prepare_for_save(self):
		for token in self.data:
			self.data[token].prepare_for_save()
			
	def fix_from_load(self):
		for token in self.data:
			self.data[token].fix_from_load()
		
	def draw(self, pygame_display, pixel_size):
		for desc in self.data:
			self.data[desc].draw(pygame_display, pixel_size)
			
	#returns name of the new item
	def make_new(self):
		if "unnamed" not in self.data:
			self.data["unnamed"] = TokenDescriptor()
			return "unnamed"
		else:
			next = 1
			name = "unnamed (" + str(next) + ")"
			while name in self.data:
				next += 1
				name = "unnamed (" + str(next) + ")"
			self.data[name] = TokenDescriptor()
			return name
			
	#returns true if successful, false if invalid
	def change_name(self, old_name, new_name):	
		if old_name in self.data and new_name not in self.data:
			self.data[new_name] = self.data[old_name]
			del self.data[old_name]
			return True
		else:
			return False
		
class TokenDescriptor:
	def __init__(self):
		self._image = None
		self._image_name = "None Selected"
		self._loc_set = [TokenLoc(0, 0)]
		
	def prepare_for_save(self):
		self._image = None
		
	def fix_from_load(self):
		if self._image_name != "None Selected":
			self._image = pygame.image.load(self._image_name)
			
		for loc in self._loc_set:
			if not hasattr(loc, "_visible"):
				loc._visible = True
		
	def set_image(self, image_path):
		self._image = pygame.image.load(image_path)
		self._image_name = image_path
		
	def unset_image(self):
		self._image = None
		self._image_name = "None Selected"
		
	def draw(self, pygame_display, pixel_size):
		if self._image:
			for loc in self._loc_set:
				loc.draw(pygame_display, self._image, pixel_size)
				
	def make_new(self):
		self._loc_set.append(TokenLoc(0, 0))
		
class TokenLoc:
	def __init__(self, tilex, tiley):
		self._tilex = tilex
		self._tiley = tiley
		self._subx = 0
		self._suby = 0
		self._visible = True
		
	def draw(self, pygame_display, image, pixel_size):	
		if self._visible:
			(x, y) = (self._tilex * pixel_size + self._subx, self._tiley * pixel_size + self._suby)
			pygame_display.blit(image, (x, y))
	
class EditorBox:
	def __init__(self, screen, template_storage):
		self._screen = screen
		self._template_storage = template_storage
		self._map_node = None
		self._node_coords = None
		
		self._window = tkinter.Tk()
		self._window.resizable(True, True)
		self._window.title("Editor")
		self._tab_control = ttk.Notebook(self._window)
		
		self._tile_editor = tkinter.Frame(self._tab_control)
		self._template_editor = tkinter.Frame(self._tab_control)
		self._painting_assist = tkinter.Frame(self._tab_control)
		self._token_manager = tkinter.Frame(self._tab_control)
		self._save_manager = tkinter.Frame(self._tab_control)
		self._options = tkinter.Frame(self._tab_control)
		
		self._tab_control.add(self._tile_editor, text="Tile Editor")
		self._tab_control.add(self._template_editor, text="Template Editor")
		self._tab_control.add(self._painting_assist, text="Painting Assist")
		self._tab_control.add(self._token_manager, text="Token Editor")
		self._tab_control.add(self._options, text="Options")
		self._tab_control.add(self._save_manager, text="Save Manager")
		self._tab_control.pack(expand=1, fill="both")
		
		self.init_template_storage()
		
		self.tile_editor()
		self.template_editor()
		self.paint_assist()
		self.token_manager()
		self.save_manager()
		self.options()
		
	def init_template_storage(self):
		first_template = [key for key in self._template_storage.data][0]
		self._current_template = tkinter.StringVar(value=first_template)
		#doesn't need to be initialized here- completely dependent on set tile
		self._tile_template_value = tkinter.StringVar()
		self._paint_template_value = tkinter.StringVar(value=first_template)
		
	def update_template_storage(self):
		if self._current_template.get() not in self._template_storage.data:
			self._current_template.set([key for key in self._template_storage.data][0])
		
		if self._tile_template_value.get() != "" and self._tile_template_value.get() not in self._template_storage.data and self._map_node:
			self._tile_template_value.set([key for key in self._template_storage.data if self._template_storage.data[key] == self._map_node._descriptor][0])
			
		if self._paint_template_value.get() not in self._template_storage.data:
			self._paint_template_value.set([key for key in self._template_storage.data][0])
			
		self._tile_template_select["values"] = [key for key in self._template_storage.data]
		self._editor_template_select["values"] = [key for key in self._template_storage.data]
		self._paint_template_select["values"] = [key for key in self._template_storage.data]
		
	def tile_editor(self):
		self._tile_editor_frame = tkinter.Frame(master=self._tile_editor)
		frame = self._tile_editor_frame
		frame.pack()
		
		self._tile_template_select = ttk.Combobox(master=frame, textvariable=self._tile_template_value, state="readonly", 
													values=[key for key in self._template_storage.data])
		self._tile_template_select.bind("<<ComboboxSelected>>", self.set_tile_template)
		
		if self._map_node == None:
			tkinter.Label(master=frame, text="No current tile.").pack()
			self._none_prev_selected = True
			return
		self._none_prev_selected = False
		#only executed if we have a true node
		self._tile_coord_value = tkinter.StringVar(value="Inspecting tile " + str(self._node_coords))
		self._tile_coord_label = tkinter.Label(master=frame, textvariable=self._tile_coord_value)
		
		self._tile_fog_value = tkinter.IntVar(value=int(self._map_node._fog_of_war))
		self._tile_fog_button = tkinter.Checkbutton(master=frame, text="Fog of War", variable=self._tile_fog_value, command=self.on_change_fog)
		
		self._vision_type_value = tkinter.StringVar(value=self._map_node._vision_type)
		self._vision_type_select = ttk.Combobox(master=frame, textvariable=self._vision_type_value, state="readonly", values=vision_types)
		self._vision_type_select.bind("<<ComboboxSelected>>", self.set_tile_vision)
		
		self._tile_note_text = tkinter.Text(frame, height=4, width=36, wrap=tkinter.WORD)
		self._tile_note_text.insert(1.0, self._map_node._notes.strip())
		self._tile_note_text.bind("<KeyRelease>", self.on_change_note)
		
		
		self._tile_coord_label.grid(row=0, column=0, columnspan=3)
		self._tile_template_select.grid(row=1, column=1)
		self._tile_fog_button.grid(row=1, column=2)
		self._vision_type_select.grid(row=2, column=1)
		self._tile_note_text.grid(row=3,column=0, columnspan=3)
			
	def on_change_note(self, *args):
		self._map_node._notes = self._tile_note_text.get(1.0, tkinter.END)
		
	def on_change_fog(self):
		self._map_node._fog_of_war = bool(self._tile_fog_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
			
	def select_tile(self, x, y):
		if self._map_node:
			self._map_node._selected = False
	
		self._node_coords = (x, y)
		self._map_node = self._screen._map.get_at(x, y)
		
		self._map_node._selected = True
		
		self._tile_template_value.set
		
		#manage paint assist
		if self._brush_mode_value.get() == 1:
			self._map_node._descriptor = self._template_storage.data[self._paint_template_value.get()]
		elif self._fill_mode_value.get() == 1 and self._map_node._descriptor != self._template_storage.data[self._paint_template_value.get()]:
			self.fill_from_tile()
		elif self._fog_mode_value.get() == 1:
			self.clear_fog_from_tile()
		
		self.refresh_tile()
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def fill_from_tile(self):
		root_template = self._map_node._descriptor
		frontier = [self._node_coords]
		iter = 0
		#loop while items are in frontier
		while frontier:
			iter += 1
			to_consider = frontier[0]
			del frontier[0]
			#get all real neighbours that 
			to_look = []
			for change in ((0, 1), (1, 0), (0, -1), (-1, 0)):
				new = (to_consider[0] + change[0], to_consider[1] + change[1])
				if new[0] >= 0 and new[0] < self._screen._map._width and new[1] >= 0 and new[1] < self._screen._map._height:
					to_look.append(new)
			#look at each and if they match the root_template add them to the frontier
			for coord in to_look:
				if self._screen._map.get_at(coord[0], coord[1])._descriptor == root_template:
					if coord not in frontier:
						frontier.append(coord)
			#color the current tile
			self._screen._map.get_at(to_consider[0], to_consider[1])._descriptor = self._template_storage.data[self._paint_template_value.get()]
			
		print("Filled " + str(iter) + " tiles.")
		#at the end, color the root tile to update the picture
		self._map_node._descriptor = self._template_storage.data[self._paint_template_value.get()]
		
	def clear_fog_from_tile(self):
		for change in ((0, 0), (0, 1), (1, 0), (0, -1), (-1, 0)):
			new = (self._node_coords[0] + change[0], self._node_coords[1] + change[1])
			#if within the map bounds
			if new[0] >= 0 and new[0] < self._screen._map._width and new[1] >= 0 and new[1] < self._screen._map._height:
				self._screen._map.get_at(new[0], new[1])._fog_of_war = False
		
	def refresh_tile(self):
		if(self._map_node != None):
			g = [key for key in self._template_storage.data if self._template_storage.data[key] == self._map_node._descriptor][0]
			self._tile_template_value.set(g)
			if(self._none_prev_selected):
				self._tile_editor_frame.destroy()
				self.tile_editor()
			else:
				self._tile_coord_value.set("Inspecting tile " + str(self._node_coords))
				self._tile_fog_value.set(int(self._map_node._fog_of_war))
				self._vision_type_value.set(self._map_node._vision_type)
				self._tile_note_text.delete(1.0, tkinter.END)
				self._tile_note_text.insert(1.0, self._map_node._notes.strip())
		elif not self._none_prev_selected:
			self._tile_editor_frame.destroy()
			self.tile_editor()
		
		# self._tile_editor_frame.destroy()
		# self.tile_editor()
		
	def set_tile_template(self, event):
		self._map_node._descriptor = self._template_storage.data[self._tile_template_value.get()]
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def set_tile_vision(self, event):
		self._map_node._vision_type = self._vision_type_value.get()
		if self._screen._show_vision:
			self._screen.draw_pygame()
			pygame.display.flip()
		
	def template_editor(self):
		self._template_editor_frame = tkinter.Frame(master=self._template_editor)
		frame = self._template_editor_frame
		frame.pack()
		
		self._editor_template_select = ttk.Combobox(master=frame, textvariable=self._current_template, state="readonly",
													values = [key for key in self._template_storage.data])
		
		self._editor_template_select.bind("<<ComboboxSelected>>", self.set_template_select)
		
		self._template_rename_label = tkinter.Label(master=frame, text="Rename template: ")
		self._template_rename_value = tkinter.StringVar(value=self._template_storage.current)
		self._template_rename_entry = tkinter.Entry(master=frame, exportselection=0, textvariable=self._template_rename_value)
		self._template_rename_button = tkinter.Button(master=frame, text="Enter", command=self.enter_new_template_name)
		
		self._new_template_button = tkinter.Button(master=frame, text="New Template", command=self.new_template)
		
		self._red_value = tkinter.StringVar(value=self._template_storage.get_c().red)
		self._red_label = tkinter.Label(master=frame, text="Red:   ")
		self._red_box = ttk.Spinbox(master=frame, from_=0, to=255, textvariable=self._red_value, wrap=True)
		self._green_value = tkinter.StringVar(value=self._template_storage.get_c().green)
		self._green_label = tkinter.Label(master=frame, text="Green: ")
		self._green_box = ttk.Spinbox(master=frame, from_=0, to=255, textvariable=self._green_value, wrap=True)
		self._blue_value = tkinter.StringVar(value=self._template_storage.get_c().blue)
		self._blue_label = tkinter.Label(master=frame, text="Blue:  ")
		self._blue_box = ttk.Spinbox(master=frame, from_=0, to=255, textvariable=self._blue_value, wrap=True)
		
		self._red_box.bind("<FocusOut>", self.red_clamp)
		self._red_box.bind("<Return>", self.red_clamp)
		self._green_box.bind("<FocusOut>", self.green_clamp)
		self._green_box.bind("<Return>", self.green_clamp)
		self._blue_box.bind("<FocusOut>", self.blue_clamp)
		self._blue_box.bind("<Return>", self.blue_clamp)
		
		self._editor_template_select.grid(row=0, column=1, columnspan=2)
		self._red_label.grid(row=1, column=0)
		self._red_box.grid(row=1, column=1)
		self._template_rename_label.grid(row=1, column=2, columnspan=2)
		self._template_rename_entry.grid(row=2, column=2)
		self._template_rename_button.grid(row=2, column=3)
		self._green_label.grid(row=2, column=0)
		self._green_box.grid(row=2, column=1)
		self._blue_label.grid(row=3, column=0)
		self._blue_box.grid(row=3, column=1)
		self._new_template_button.grid(row=3, column=2, columnspan=2)
		
	def set_template_select(self, event):
		self.red_clamp(None)
		self.green_clamp(None)
		self.blue_clamp(None)
	
		self._template_storage.current = self._current_template.get()
		self._red_value.set(self._template_storage.get_c().red)
		self._green_value.set(self._template_storage.get_c().green)
		self._blue_value.set(self._template_storage.get_c().blue)
		self._template_rename_value.set(self._current_template.get())
		
	def enter_new_template_name(self):
		if(self._template_rename_value.get() in self._template_storage.data):
			self.make_pop_up_message("Template already has that name.", "Warning")
			return
		#update paint assist selection
		if self._paint_template_value.get() == self._template_storage.current:
			self._paint_template_value.set(self._template_rename_value.get())
			
		d = self._template_storage.data[self._template_storage.current]
		del self._template_storage.data[self._template_storage.current]
		self._template_storage.data[self._template_rename_value.get()] = d
		self._template_storage.current = self._template_rename_value.get()
		
		self._current_template.set(self._template_storage.current)
		
		self.update_template_storage()
			
	def new_template(self):
		self._template_storage.make_new()
		self._current_template.set(self._template_storage.current)
		self._red_value.set(self._template_storage.get_c().red)
		self._green_value.set(self._template_storage.get_c().green)
		self._blue_value.set(self._template_storage.get_c().blue)
		self._template_rename_value.set(self._current_template.get())
		
		self.update_template_storage()
		
	def red_clamp(self, event):
		if not self._red_value.get().isdigit:
			self._red_value.set(0)
		else:
			self._red_value.set(str(max(0, min(255, int(self._red_value.get())))))
			
		self._template_storage.data[self._template_storage.current].red = int(self._red_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def green_clamp(self, event):
		if not self._green_value.get().isdigit:
			self._green_value.set(0)
		else:
			self._green_value.set(str(max(0, min(255, int(self._green_value.get())))))
			
		self._template_storage.data[self._template_storage.current].green = int(self._green_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def blue_clamp(self, event):
		if not self._blue_value.get().isdigit:
			self._blue_value.set(0)
		else:
			self._blue_value.set(str(max(0, min(255, int(self._blue_value.get())))))
			
		self._template_storage.data[self._template_storage.current].blue = int(self._blue_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def paint_assist(self):
		self._painting_assist_frame = tkinter.Frame(master=self._painting_assist)
		frame = self._painting_assist_frame
		frame.pack()
		
		self._paint_template_select = ttk.Combobox(master=frame, textvariable=self._paint_template_value, state="readonly",
													values=[key for key in self._template_storage.data])
		
		self._none_mode_value = tkinter.IntVar(value=1)
		self._brush_mode_value = tkinter.IntVar(value=0)
		self._fill_mode_value = tkinter.IntVar(value=0)
		self._fog_mode_value = tkinter.IntVar(value=0)
		self._none_mode_button = tkinter.Checkbutton(master=frame, text="No Mode", variable=self._none_mode_value, command=self.set_none_mode)
		self._brush_mode_button = tkinter.Checkbutton(master=frame, text="Brush Mode", variable=self._brush_mode_value, command=self.set_brush_mode)
		self._fill_mode_button = tkinter.Checkbutton(master=frame, text="Fill Mode", variable=self._fill_mode_value, command=self.set_fill_mode)
		self._fog_mode_button = tkinter.Checkbutton(master=frame, text="Clear Fog Mode", variable=self._fog_mode_value, command=self.set_fog_mode)
		
		self._paint_template_select.grid(row=1, column=1)
		self._none_mode_button.grid(row=2, column=0)
		self._brush_mode_button.grid(row=2, column=1)
		self._fill_mode_button.grid(row=2, column=2)
		self._fog_mode_button.grid(row=3, column=1)
		
	def clear_mode(self):
		self._brush_mode_value.set(0)
		self._fill_mode_value.set(0)
		self._none_mode_value.set(0)
		self._fog_mode_value.set(0)
		
	def set_none_mode(self):
		self.clear_mode()
		self._none_mode_value.set(1)
		
	def set_brush_mode(self):
		if not self._brush_mode_value.get():
			self.set_none_mode()
		else:
			self.clear_mode()
			self._brush_mode_value.set(1)
			
	def set_fill_mode(self):
		if not self._fill_mode_value.get():
			self.set_none_mode()
		else:
			self.clear_mode()
			self._fill_mode_value.set(1)
			
	def set_fog_mode(self):
		if not self._fog_mode_value.get():
			self.set_none_mode()
		else:
			self.clear_mode()
			self._fog_mode_value.set(1)
		
	def token_manager(self):
		self._token_manager_frame = tkinter.Frame(master=self._token_manager)
		frame = self._token_manager_frame
		frame.pack()
		storage = self._screen._token_storage
		
		#init current token to the first token
		self._current_token = tkinter.StringVar(value=[d for d in storage.data][0])
		self._token_select = ttk.Combobox(master=frame, textvariable=self._current_token, state="readonly", values=[key for key in storage.data])
		self._token_select.bind("<<ComboboxSelected>>", self.set_token_select)
		
		self._image_path_value = tkinter.StringVar(value=storage.data[self._current_token.get()]._image_name.split("/")[-1].split("\\")[-1])
		self._image_path_label = tkinter.Label(master=frame, textvariable=self._image_path_value)
		self._image_set_button = tkinter.Button(master=frame, text="Set Image", command=self.select_image_to_open)
		
		self._token_name_label = tkinter.Label(master=frame, text="Rename token: ")
		self._token_name_value = tkinter.StringVar(value=self._current_token.get())
		self._token_name_entry = tkinter.Entry(master=frame, exportselection=0, textvariable=self._token_name_value)
		self._token_name_button = tkinter.Button(master=frame, text="Enter", command=self.enter_token_name)
		
		self._new_token_button = tkinter.Button(master=frame, text="New Token", command=self.new_token)
		self._del_token_button = tkinter.Button(master=frame, text="Delete Token", command=self.del_token)
		
		self._sub_token_label = tkinter.Label(master=frame, text="Current Subtoken: ")
		self._current_sub_token = tkinter.StringVar(value="1")
		self._sub_token_select = ttk.Combobox(master=frame, textvariable=self._current_sub_token, state="readonly",
												values=[str(i+1) for i in range(0, len(storage.data[self._current_token.get()]._loc_set))])
		self._sub_token_select.bind("<<ComboboxSelected>>", self.set_sub_token_select)
		
		self._new_sub_token_button = tkinter.Button(master=frame, text="New Subtoken", command=self.new_sub_token)
		self._del_sub_token_button = tkinter.Button(master=frame, text="Delete Subtoken", command=self.del_sub_token)
		
		self._sub_token_x_label = tkinter.Label(master=frame, text="x: ")
		self._sub_token_x_value = tkinter.StringVar(value=storage.data[self._current_token.get()]._loc_set[int(self._current_sub_token.get())-1]._tilex)
		self._sub_token_x_box = ttk.Spinbox(master=frame, from_=0, to=self._screen._map._width-1, textvariable=self._sub_token_x_value, wrap=True)
		self._sub_token_x_box.bind("<Return>", self.clamp_sub_token)
		self._sub_token_x_box.bind("<FocusOut>", self.clamp_sub_token)
		
		self._sub_token_y_label = tkinter.Label(master=frame, text="y: ")
		self._sub_token_y_value = tkinter.StringVar(value=storage.data[self._current_token.get()]._loc_set[int(self._current_sub_token.get())-1]._tiley)
		self._sub_token_y_box = ttk.Spinbox(master=frame, from_=0, to=self._screen._map._height-1, textvariable=self._sub_token_y_value, wrap=True)
		self._sub_token_y_box.bind("<Return>", self.clamp_sub_token)
		self._sub_token_y_box.bind("<FocusOut>", self.clamp_sub_token)
		
		self._sub_token_vis_value = tkinter.IntVar(value=int(storage.data[self._current_token.get()]._loc_set[int(self._current_sub_token.get())-1]._visible))
		self._sub_token_vis_box = tkinter.Checkbutton(master=frame, text="Visible", variable=self._sub_token_vis_value, command=self.update_visible)
		
		self._go_to_cursor_button = tkinter.Button(master=frame, text="Go to Selected", command=self.jump_sub_token)
		
		self._token_select.grid(row=0, column=0, columnspan=3)
		self._image_path_label.grid(row=1, column=0, columnspan=3)
		self._image_set_button.grid(row=2, column=0, columnspan=3)
		self._token_name_label.grid(column=0, row=3)
		self._token_name_entry.grid(column=1, row=3)
		self._token_name_button.grid(column=2, row=3)
		self._new_token_button.grid(column=0, row=4, columnspan=1)
		self._del_token_button.grid(column=1, row=4, columnspan=2)
		self._sub_token_label.grid(row=0, column=3)
		self._sub_token_select.grid(row=0, column=4)
		self._new_sub_token_button.grid(row=1, column=3)
		self._del_sub_token_button.grid(row=1, column=4)
		self._sub_token_x_label.grid(row=2, column=3)
		self._sub_token_x_box.grid(row=2, column=4)
		self._sub_token_y_label.grid(row=3, column=3)
		self._sub_token_y_box.grid(row=3, column=4)
		self._sub_token_vis_box.grid(row=4, column=3)
		self._go_to_cursor_button.grid(row=4, column=4)
		
	def on_load_tokens(self):
		self._current_token.set([key for key in self._screen._token_storage.data][0])
		self._token_select["values"] = [key for key in self._screen._token_storage.data]
		self.set_token_select(None)
		
	def set_token_select(self, event):
		self._token_name_value.set(self._current_token.get())
		self._image_path_value.set(self._screen._token_storage.data[self._current_token.get()]._image_name.split("/")[-1].split("\\")[-1])
		self._current_sub_token.set("1")
		self.update_sub_token_side()
		
	def enter_token_name(self):
		if(self._token_name_value.get() in self._screen._token_storage.data):
			self.make_pop_up_message("Token already has that name.", "Warning")
			return
		self._screen._token_storage.change_name(self._current_token.get(), self._token_name_value.get())
		
		self._current_token.set(self._token_name_value.get())
		self._token_select["values"] = [key for key in self._screen._token_storage.data]
		
	def new_token(self):
		new_name = self._screen._token_storage.make_new()
		
		self._current_token.set(new_name)
		self._token_select["values"] = [key for key in self._screen._token_storage.data]
		
		self.set_token_select(None)
		
	def del_token(self):
		if(len([key for key in self._screen._token_storage.data]) <= 1):
			self.make_pop_up_message("Can't delete the last token.", "Warning")
			return
	
		self._token_confirm = tkinter.Toplevel(master=self._window)
		self._token_confirm.title("Warning")
		tkinter.Label(master=self._token_confirm, text="Are you sure you want to delete this token?").grid(row=0, column=0, columnspan=2)
		tkinter.Button(master=self._token_confirm, text="No", command=self._token_confirm.destroy).grid(row=1,column=1)
		tkinter.Button(master=self._token_confirm, text="Yes", command=self.confirm_del_token).grid(row=1,column=0)
		
	def confirm_del_token(self):
		self._token_confirm.destroy()
		
		del self._screen._token_storage.data[self._current_token.get()]
		self._current_token.set([key for key in self._screen._token_storage.data][0])
		self._token_select["values"] = [key for key in self._screen._token_storage.data]
		self.set_token_select(None)
		
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def set_sub_token_select(self, event):
		print("selected sub token")
		
		self.update_sub_token_side()
		
	def select_image_to_open(self):
		file_select = filedialog.askopenfilename(master=self._token_manager_frame, title="Select Image", filetypes=((png_desc,"*.png",),(jpg_desc,"*.jpg")))
		
		if file_select == "":
			return
		else:
			self._screen._token_storage.data[self._current_token.get()].set_image(file_select)
			self._image_path_value.set(file_select.split("/")[-1].split("\\")[-1])
			self._screen.draw_pygame()
			pygame.display.flip()
		
	def new_sub_token(self):
		self.clamp_sub_token(None)
	
		self._screen._token_storage.data[self._current_token.get()].make_new()
		self._current_sub_token.set(str(len(self._screen._token_storage.data[self._current_token.get()]._loc_set)))
		self.update_sub_token_side()
		
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def del_sub_token(self):
		current_token = self._screen._token_storage.data[self._current_token.get()]
		
		if len(current_token._loc_set) > 1:
			del current_token._loc_set[int(self._current_sub_token.get())-1]
			self._current_sub_token.set("1")
			self.update_sub_token_side()
			
			self._screen.draw_pygame()
			pygame.display.flip()
		
		
	def update_sub_token_side(self):
		self._sub_token_select["values"] = [str(i+1) for i in range(0, len(self._screen._token_storage.data[self._current_token.get()]._loc_set))]
		
		current_sub = self._screen._token_storage.data[self._current_token.get()]._loc_set[int(self._current_sub_token.get())-1]
		
		self._sub_token_x_value.set(str(current_sub._tilex))
		self._sub_token_y_value.set(str(current_sub._tiley))
		self._sub_token_vis_value.set(int(current_sub._visible))
		
	def update_visible(self):
		self._screen._token_storage.data[self._current_token.get()]._loc_set[int(self._current_sub_token.get())-1]._visible = bool(self._sub_token_vis_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def jump_sub_token(self):
		self._sub_token_x_value.set(str(self._node_coords[0]))
		self._sub_token_y_value.set(str(self._node_coords[1]))
		
		self.clamp_sub_token(None)
		
	def clamp_sub_token(self, event):
		storage = self._screen._token_storage
	
		if not self._sub_token_x_value.get().isdigit():
			self._sub_token_x_value.set(0)
		else:
			self._sub_token_x_value.set(str(min(self._screen._map._width-1, max(0, int(self._sub_token_x_value.get())))))
		storage.data[self._current_token.get()]._loc_set[int(self._current_sub_token.get())-1]._tilex = int(self._sub_token_x_value.get())
		
		if not self._sub_token_y_value.get().isdigit():
			self._sub_token_y_value.set(0)
		else:
			self._sub_token_y_value.set(str(min(self._screen._map._height-1, max(0, int(self._sub_token_y_value.get())))))
		storage.data[self._current_token.get()]._loc_set[int(self._current_sub_token.get())-1]._tiley = int(self._sub_token_y_value.get())
		
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def save_manager(self):
		self._save_manager_frame = tkinter.Frame(master=self._save_manager)
		frame = self._save_manager_frame
		frame.pack()
		
		self._save_button = tkinter.Button(master=frame, text="Save Map", command=self.save_map_now)
		self._load_button = tkinter.Button(master=frame, text="Load Map", command=self.select_save_to_open)
		
		self._save_button.grid(row=1, column=1)
		self._load_button.grid(row=1, column=2)
		
	def save_map_now(self):
		file_select = filedialog.askopenfilename(master=self._save_manager_frame, title="Select file to save to", filetypes=(("Pickle files","*.pckl"),("All files","*.*")))
		
		if file_select == "":
			self.make_pop_up_message("No file has been selected", "Warning")
			return
		elif not file_select.endswith(".pckl"):
			self.make_pop_up_message("An invalid file has been selected", "Warning")
			return
			
		with open(file_select, "wb+") as f:
			self._screen._map.prepare_for_save(self._template_storage)
			self._screen._token_storage.prepare_for_save()
			pickle.dump(self._template_storage, f)
			pickle.dump(self._screen._map, f)
			pickle.dump(self._screen._token_storage, f)
			self._screen._map.fix_from_load(self._template_storage)
			self._screen._token_storage.fix_from_load()
		
	def select_save_to_open(self):
		self._to_load = filedialog.askopenfilename(master=self._save_manager_frame, title="Select save to open", filetypes=(("Pickle files", ".pckl"),("All files","*.*")))
			
		if self._to_load == "":
			self.make_pop_up_message("No file has been selected", "Warning")
			return
		elif not self._to_load.endswith(".pckl"):
			self.make_pop_up_message("An invalid file has been selected", "Warning")
			return
			
		self._confirm = tkinter.Toplevel(master=self._window)
		self._confirm.title("Warning")
		tkinter.Label(master=self._confirm, text="Are you sure you want to load this file?\nAll data will be lost.").grid(row=0, column=0, columnspan=2)
		tkinter.Button(master=self._confirm, text="No", command=self._confirm.destroy).grid(row=1,column=1)
		tkinter.Button(master=self._confirm, text="Yes", command=self.confirm_load).grid(row=1,column=0)
			
	def confirm_load(self):
		self._confirm.destroy()
		
		with open(self._to_load, "rb") as f:
			template_storage = pickle.load(f)
			map = pickle.load(f)
			token_storage = None
			try:
				token_storage = pickle.load(f)
			except:
				print("save has no token storage.")
				token_storage = TokenStorage()
			map.fix_from_load(template_storage)
			token_storage.fix_from_load()
			self._map_node = None
			self._node_coords = None
			del self._template_storage
			del self._screen._map
			self._template_storage = template_storage
			self._screen._map = map
			self._screen._token_storage = token_storage
			
		self.on_load_tokens()
		self._current_template.set(self._template_storage.current)
		self._red_value.set(self._template_storage.get_c().red)
		self._green_value.set(self._template_storage.get_c().green)
		self._blue_value.set(self._template_storage.get_c().blue)
		self._template_rename_value.set(self._current_template.get())
			
		self.update_template_storage()
		self.refresh_tile()
		
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def options(self):
		self._options_frame = tkinter.Frame(self._options)
		frame = self._options_frame
		frame.pack()
		
		self._lines_option_value = tkinter.IntVar(value=int(self._screen._lines))
		self._lines_option_box = tkinter.Checkbutton(frame, text="Border Lines",variable=self._lines_option_value,command=self.lines_update)
		self._fog_option_value = tkinter.IntVar(value=int(self._screen._fog_enabled))
		self._fog_option_box = tkinter.Checkbutton(frame, text="Fog of War",variable=self._fog_option_value,command=self.fog_update)
		self._reset_fog_button = tkinter.Button(frame, text="Reset Fog of War", command=self.reset_fog)
		self._highlight_option_value = tkinter.IntVar(value=int(self._screen._select_highlight))
		self._highlight_option_box = tkinter.Checkbutton(frame, text="Highlight Selected",variable=self._highlight_option_value, command=self.highlights_update)
		self._export_display_button = tkinter.Button(frame, text="Screenshot", command=self._screen.export_display)
		self._notes_option_value = tkinter.IntVar(value=int(self._screen._show_notes))
		self._notes_option_box = tkinter.Checkbutton(frame, text="Indicate Notes",variable=self._notes_option_value,command=self.notes_update)
		self._tokens_option_value = tkinter.IntVar(value=int(self._screen._show_tokens))
		self._tokens_option_box = tkinter.Checkbutton(frame, text="Show Tokens", variable=self._tokens_option_value, command=self.show_token_option)
		self._double_line_value = tkinter.IntVar(value=int(self._screen._double_width_lines))
		self._double_line_box = tkinter.Checkbutton(frame, text="Wide Border Lines",variable=self._double_line_value,command=self.doubled_update)
		self._vision_option_value = tkinter.IntVar(value=int(self._screen._show_vision))
		self._vision_option_box = tkinter.Checkbutton(frame, text="Show Vision Types",variable=self._vision_option_value,command=self.vision_update)
		
		self._lines_option_box.grid(row=1,column=0)
		self._fog_option_box.grid(row=1, column=1)
		self._vision_option_box.grid(row=1, column=2)
		self._reset_fog_button.grid(row=4,column=1)
		self._highlight_option_box.grid(row=2, column=0)
		self._notes_option_box.grid(row=2, column=1)
		self._tokens_option_box.grid(row=3, column=0)
		self._double_line_box.grid(row=3, column=1)
		self._export_display_button.grid(row=4, column=0)
			
	def lines_update(self):
		self._screen._lines = bool(self._lines_option_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
			
	def fog_update(self):
		self._screen._fog_enabled = bool(self._fog_option_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
			
	def notes_update(self):
		self._screen._show_notes = bool(self._notes_option_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
			
	def reset_fog(self):
		for y in range(0, self._screen._map._height):
			for x in range(0, self._screen._map._width):
				self._screen._map.get_at(x, y)._fog_of_war = True
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def highlights_update(self):
		self._screen._select_highlight = bool(self._highlight_option_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def show_token_option(self):
		self._screen._show_tokens = bool(self._tokens_option_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def doubled_update(self):
		self._screen._double_width_lines = bool(self._double_line_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
		
	def vision_update(self):
		self._screen._show_vision = bool(self._vision_option_value.get())
		self._screen.draw_pygame()
		pygame.display.flip()
			
	def make_pop_up_message(self, message, title="Message"):
		pop_up = tkinter.Toplevel(master=self._window)
		pop_up.title(title)
		tkinter.Label(master=pop_up, text=message).grid(row=0)
		tkinter.Button(master=pop_up, text="Dismiss", command=pop_up.destroy).grid(row=1)
		
#misc helper function lmoa
def is_int_str(string):
    return (
        string.startswith(('-', '+')) and string[1:].isdigit()
    ) or string.isdigit()
	
if __name__ == "__main__":
	pygame.init()
	map = Map(45, 45)
	screen = Screen(map)
	
	screen.init_pygame()
	screen.draw_pygame()
	
	pygame.display.flip()
	editor = EditorBox(screen, TemplateStorage())
	
	map.apply_base_descriptor(editor._template_storage.data["unnamed"])
	
	while True:
		editor._window.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				editor._window.destroy()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				editor.select_tile(pos[0]//screen._pixel_size, pos[1]//screen._pixel_size)