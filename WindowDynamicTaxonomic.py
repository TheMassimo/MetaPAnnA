#import config module for environmental variability
import config
#import my utility class and function
import MyUtility
#import my multi threading function to upload and download file
from MyMultiThreading import *

#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showinfo
#pandas import
import pandas as pd
#random import
import random
#importo os
import os

# importing the threading module
from threading import Thread

#import loading window
import WindowLoading as wLd
#import next window
import WindowFunctionalMenu as wFnMn

class DynamicTaxonomicWindow(tk.Toplevel): #tk.Tk):
  def __init__(self, wn_root, wn_previous, previousDf):
    super().__init__()

    #change icon
    img = PhotoImage(file=resource_path(config.icon))
    self.iconphoto(False, img)

    #take the root window
    self.wn_root = wn_root
    #take the previous window
    self.wn_previous = wn_previous

    #take the old df
    self.df = previousDf;
    #check if file is load
    self.isFileLoad = False

    #preapre df
    self.df_annotation = pd.DataFrame()

    # configure the root window
    self.title('Taxonomic annotation')

    
    ### left area ###
    #Load/download frame
    self.frame_left = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_left.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
    #Load button
    self.btn_loadFile = tk.Button(self.frame_left, text='Upload annotation file', font=config.font_button, width=20, command=self.upload_file)
    self.btn_loadFile.grid(row=0, column=0, padx=5, pady=5)
    #label template
    self.lbl_loadedFile = tk.Label(self.frame_left, text='No file',width=30,font=config.font_up_base)
    self.lbl_loadedFile.grid(row=1, column=0, padx=5, pady=5)
    #Download button
    self.btn_download = tk.Button(self.frame_left, text='Download annotated table', font=config.font_button, width=20,command=self.download)
    self.btn_download.grid(row=2, column=0, padx=5, pady=5)
    #Fill with unassigned
    self.var_chc_unassigned = IntVar(value=0)
    self.chc_unassigned = tk.Checkbutton(self.frame_left, text='Replace missing values with \'unassigned\'',
                                         width=34, anchor="w", variable=self.var_chc_unassigned, onvalue=1, offvalue=0)
    self.chc_unassigned.grid(row=3, column=0, padx=5, pady=10)
    self.chc_unassigned.config(font = config.font_checkbox )
    #Equate I and L
    if( (MyUtility.workDict["mode"] != 'Proteins') and (MyUtility.workDict['taxonomic_match'] == 'peptide')):
      self.var_chc_IandL = IntVar(value=0)
      self.chc_IandL = tk.Checkbutton(self.frame_left, text='I and L treated as equivalent for annotation',
                                           width=34, anchor="w", variable=self.var_chc_IandL, onvalue=1, offvalue=0)
      self.chc_IandL.grid(row=4, column=0, padx=5, pady=10)
      self.chc_IandL.config(font = config.font_checkbox )

    ### centre area ###
    #title frame    
    self.frame_centre = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_centre.grid(row=0, column=1, padx=2, pady=2,sticky="nsew")

    #title of editing
    self.lbl_fileter = tk.Label(self.frame_centre,text='Column selection',width=20,font=config.font_title)  
    self.lbl_fileter.grid(row=0, column=0, columnspan=2, padx=6, pady=6, sticky='ew')

    #riquadro con le colonne da scegliere
    self.make_columnsHeaders(p_row=1, p_column=0, p_rowspan=2, p_sticky='n')

    if(MyUtility.workDict['mode'] == 'Proteins'):
      self.make_proteinAccession(p_row=1, p_column=1, p_name='Protein Accessions', p_sticky='n')
    else:
      if(MyUtility.workDict['taxonomic_match'] == 'protein'):
        self.make_proteinAccession(p_row=1, p_column=1, p_name='Protein Accessions', p_sticky='n')
      else: #peptide
        self.make_peptideSequence(p_row=1, p_column=1, p_sticky='n')

    self.make_chosenColumns(p_row=2, p_column=1, p_rowspan=1, p_sticky='n')


    ### down area ###
    self.frame_down = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_down.grid(row=1, column=0, columnspan=2, padx=2, pady=(2,10), sticky="nsew")
    self.frame_down.columnconfigure(0, weight=1)
    self.frame_down.columnconfigure(1, weight=1)
    self.frame_down.columnconfigure(2, weight=1)
    #Previous Step
    self.btn_previous_step = tk.Button(self.frame_down, text='← Previous step', font=config.font_button, width=20, command=self.previous_window)
    self.btn_previous_step.grid(row=0, column=0, padx=20, pady=5, sticky="w")
    #Next Step
    self.btn_next_step = tk.Button(self.frame_down, text='Next step →', font=config.font_button, width=20, command=self.next_window)
    self.btn_next_step.grid(row=0, column=2, padx=20, pady=5, sticky="e")

    #put this window up
    self.lift()

    #when I close window
    self.protocol("WM_DELETE_WINDOW", self.on_closing)
  

  def make_columnsHeaders(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Columns Headers frame
    self.frame_columnsHeaders = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_columnsHeaders.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_columnHeaders = tk.Label(self.frame_columnsHeaders, text='Column headers', width=32, font=config.font_subtitle )  
    self.lbl_columnHeaders.grid(row=0, column=0, padx=6, pady=6)

    #Create frame and scrollbar
    self.all_columns_frame = Frame(self.frame_columnsHeaders)#, bg='red')
    self.all_columns_frame.grid(row=1, column=0, rowspan=1)
    #scrollbar
    self.all_columns_scrollbar = Scrollbar(self.all_columns_frame,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.all_columns_listbox = Listbox(self.all_columns_frame, yscrollcommand=self.all_columns_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.all_columns_listbox.grid(row=0, column=0)
    self.all_columns_listbox.config(width=40, height=20)
    #configure scrollvar
    self.all_columns_scrollbar.config(command=self.all_columns_listbox.yview)
    self.all_columns_scrollbar.grid(row=0, column=1, sticky="NS")

  def make_proteinAccession(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_name='', p_sticky='nsew'):
    #protein Accession frame
    self.frame_proteinAccession = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_proteinAccession.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_proteinAccession = tk.Label(self.frame_proteinAccession, text=p_name, width=32, font=config.font_subtitle )  
    self.lbl_proteinAccession.grid(row=0, column=0, columnspan=2, padx=6, pady=2)

    #button select >
    self.btn_take_proteinAccession = tk.Button(self.frame_proteinAccession, text='>', font=config.font_button,
                                               width=2, command=lambda: self.take_column(self.proteinAccession_listbox))
    self.btn_take_proteinAccession.grid(row=1, column=0, padx=1, pady=1)
    #button unselect <
    self.btn_restore_proteinAccession = tk.Button(self.frame_proteinAccession, text='<', font=config.font_button,
                                                  width=2, command=lambda: self.restore_column(self.proteinAccession_listbox))
    self.btn_restore_proteinAccession.grid(row=2, column=0, padx=1, pady=1)

    #Create frame and scrollbar
    self.all_proteinAccession = Frame(self.frame_proteinAccession)#, bg='red')
    self.all_proteinAccession.grid(row=1, column=1, rowspan=2, padx=1, pady=1)
    #scrollbar
    self.proteinAccession_scrollbar = Scrollbar(self.all_proteinAccession,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.proteinAccession_listbox = Listbox(self.all_proteinAccession, yscrollcommand=self.proteinAccession_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.proteinAccession_listbox.grid(row=0, column=0)
    self.proteinAccession_listbox.config(width=40, height=4)
    #configure scrollvar
    self.proteinAccession_scrollbar.config(command=self.proteinAccession_listbox.yview)
    self.proteinAccession_scrollbar.grid(row=0, column=1, sticky="NS")

  def make_peptideSequence(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #protein Accession frame
    self.frame_peptideSequence = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_peptideSequence.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_peptideSequence = tk.Label(self.frame_peptideSequence, text='Sequence', width=32, font=config.font_subtitle )  
    self.lbl_peptideSequence.grid(row=0, column=0, columnspan=2, padx=6, pady=6)

    #button select >
    self.btn_take_peptideSequence = tk.Button(self.frame_peptideSequence, text='>', font=config.font_button,
                                              width=2, command=lambda: self.take_column(self.peptideSequence_listbox))
    self.btn_take_peptideSequence.grid(row=1, column=0, padx=1, pady=1)
    #button unselect <
    self.btn_restore_peptideSequence = tk.Button(self.frame_peptideSequence, text='<', font=config.font_button,
                                                 width=2, command=lambda: self.restore_column(self.peptideSequence_listbox))
    self.btn_restore_peptideSequence.grid(row=2, column=0, padx=1, pady=1)

    #Create frame and scrollbar
    self.all_peptideSequence = Frame(self.frame_peptideSequence)#, bg='red')
    self.all_peptideSequence.grid(row=1, column=1, rowspan=2, padx=1, pady=1)
    #scrollbar
    self.peptideSequence_scrollbar = Scrollbar(self.all_peptideSequence,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.peptideSequence_listbox = Listbox(self.all_peptideSequence, yscrollcommand=self.peptideSequence_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.peptideSequence_listbox.grid(row=0, column=0)
    self.peptideSequence_listbox.config(width=40, height=5)
    #configure scrollvar
    self.peptideSequence_scrollbar.config(command=self.peptideSequence_listbox.yview)
    self.peptideSequence_scrollbar.grid(row=0, column=1, sticky="NS")
 
  def make_chosenColumns(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #protein Accession frame
    self.frame_chosenColumns = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_chosenColumns.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_taxonomicColumns = tk.Label(self.frame_chosenColumns, text='Taxonomic annotations', width=32, font=config.font_subtitle )  
    self.lbl_taxonomicColumns.grid(row=0, column=0, columnspan=2, padx=6, pady=6)

    #button select >
    self.btn_take_columns = tk.Button(self.frame_chosenColumns, text='>', font=config.font_button,
                                               width=2, command=lambda: self.take_column(self.chosenColumns_listbox))
    self.btn_take_columns.grid(row=1, column=0, padx=1, pady=1)
    #button unselect <
    self.btn_restore_columns = tk.Button(self.frame_chosenColumns, text='<', font=config.font_button,
                                                  width=2, command=lambda: self.restore_column(self.chosenColumns_listbox))
    self.btn_restore_columns.grid(row=2, column=0, padx=1, pady=1)

    #Create frame and scrollbar
    self.all_chosenColumns = Frame(self.frame_chosenColumns)#, bg='red')
    self.all_chosenColumns.grid(row=1, column=1, rowspan=2, padx=1, pady=1)
    #scrollbar
    self.chosenColumns_scrollbar = Scrollbar(self.all_chosenColumns,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.chosenColumns_listbox = Listbox(self.all_chosenColumns, yscrollcommand=self.chosenColumns_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.chosenColumns_listbox.grid(row=0, column=0)
    self.chosenColumns_listbox.config(width=40, height=10)
    #configure scrollvar
    self.chosenColumns_scrollbar.config(command=self.chosenColumns_listbox.yview)
    self.chosenColumns_scrollbar.grid(row=0, column=1, sticky="NS")
  
  def take_column(self, recipient_listbox):
    #I prevent it from putting more than one element in the Protein Accession or Peptide Sequence or sampleID
    if( (hasattr(self, 'proteinAccession_listbox') and (recipient_listbox == self.proteinAccession_listbox)) or
        (hasattr(self, 'peptideSequence_listbox')  and (recipient_listbox == self.peptideSequence_listbox)) ):
      if(len(self.all_columns_listbox.curselection()) > 1):
        tk.messagebox.showerror(parent=self, title="Error", message="Select only 1 item for this area")
        return
      elif(recipient_listbox.size() > 0):
        tk.messagebox.showerror(parent=self, title="Error", message="This area can only have 1 associated column")
        return

    #Move the elements to the various areas and remove them from the main one
    #remove the elements from the starting listbox
    items_to_move = []
    for index in reversed(self.all_columns_listbox.curselection()):
      #add elemnts to list for recipient listbox
      items_to_move.append(self.all_columns_listbox.get(index))
      #remove element to all columns listbox
      self.all_columns_listbox.delete(index)
    #add elements to recipient listbox
    for el in reversed(items_to_move):
      recipient_listbox.insert(END, el)

  def restore_column(self, sender_listbox):
    #Move the elements to the various areas and remove them from the main one
    #remove the elements from the starting listbox
    items_to_move = []
    for index in reversed(sender_listbox.curselection()):
      #add elemnts to list for sender listbox
      items_to_move.append(sender_listbox.get(index))
      #remove element to all columns listbox
      sender_listbox.delete(index)
    #add elements to recipient listbox
    for el in reversed(items_to_move):
      self.all_columns_listbox.insert(END, el)

  def on_closing(self):
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
      self.wn_root.destroy()

  def monitor_upload(self, thread):
    if thread.is_alive():
      # check the thread every 100ms
      self.after(100, lambda: self.monitor_upload(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(thread.fileOpen):
        #take the df_annotation
        self.df_annotation = thread.df
        #read it to create some button in the window and mark if the file is load
        self.isFileLoad = self.manage_the_upload()
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="File not uploaded\nIt is probably in use by another program")

  def monitor_download(self, thread):
    if thread.is_alive():
      #check the thread every 100ms
      self.after(100, lambda: self.monitor_download(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(not thread.fileSaved):
        tk.messagebox.showerror(parent=self, title="Error", message="File not saved\nIt is probably in use by another program")

  def manage_the_upload(self):
    #if need clear previous listbox
    if( hasattr(self, 'proteinAccession_listbox') ):
      self.proteinAccession_listbox.delete(0, END)
    if( hasattr(self, 'peptideSequence_listbox') ):
      self.peptideSequence_listbox.delete(0, END)
    if( hasattr(self, 'chosenColumns_listbox') ):
      self.chosenColumns_listbox.delete(0, END)

    #if listbox is not empty then clear all
    if self.all_columns_listbox.size() > 0:
        # rimozione di tutti gli elementi dalla ListBox
        self.all_columns_listbox.delete(0, END)

    #fill_listbox with all columns
    columns = self.df_annotation.columns.tolist()
    for column in columns:
      self.all_columns_listbox.insert(END, column)

    return True

  def upload_file(self):
    #ask file name
    filepath = filedialog.askopenfilename(parent=self, title="Open",filetypes=config.file_types)

    #check if a file has been chosen
    if filepath:
      #load the name of file in label (if name is too long then resize it)
      tmp_path = os.path.basename(filepath)
      if(len(tmp_path)>25):
        tmp_path = tmp_path[:25] + "..."
      self.lbl_loadedFile['text'] = tmp_path
      #self.lbl_loadedFile['text'] = os.path.basename(filepath)

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Uploading file...")

      #create thread to load file
      upload_thread = AsyncUpload(filepath)
      upload_thread.start()
      self.monitor_upload(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

  def monitor_manage_file(self, thread, next_command):
    if thread.is_alive():
      # check the thread every 100ms
      self.after(100, lambda: self.monitor_manage_file(thread, next_command))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(next_command == "download"):
        self.ultimate_download()
      elif(next_command == "next_window"):
        self.ultimate_next_window()

  def final_checks(self):
    #cotrols to check if the choose columns are good enough
    if( hasattr(self, 'proteinAccession_listbox') ):
      if(self.proteinAccession_listbox.size() != 1):
        tk.messagebox.showerror(parent=self, title="Error", message="Protein Accession must have 1 attribute")
        return False
    if( hasattr(self, 'peptideSequence_listbox') ):
      if(self.peptideSequence_listbox.size() != 1):
        tk.messagebox.showerror(parent=self, title="Error", message="Peptide Sequence must have 1 attribute")
        return False
    if( hasattr(self, 'chosenColumns_listbox') ):
      if(self.chosenColumns_listbox.size() < 1):
        tk.messagebox.showerror(parent=self, title="Error", message="Taxonomic annotations must have at least 1 attribute")
        return False

    #return true if all is okay
    return True

  def download(self):
    #check if file is loadid
    if(self.isFileLoad):
      #Check if value are right
      if(not self.final_checks()):
        return

      #ask directory to save file
      file_path = filedialog.asksaveasfilename(parent=self, filetypes=config.file_types, defaultextension=".xlsx")

      #check if a file has been chosen
      if file_path:
        #save file temporaneous
        self.file_path = file_path

        #show loading windows
        self.winLoad = wLd.LoadingWindow("Managing file...")
        
        #create thread to manage the file
        manage_file_thread = ManageTaxonomicDynamic(self)
        manage_file_thread.start()
        self.monitor_manage_file(manage_file_thread, "download")
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="No directory selected")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_download(self):
    #show loading windows
    self.winLoad = wLd.LoadingWindow("Downloading file...")

    #create thread to download file
    download_thread = AsyncDownload(self.df_tmp, self.file_path)
    download_thread.start()
    self.monitor_download(download_thread)

  def previous_window(self):
    #hide this window
    #self.withdraw()
    #Destroy this window
    self.destroy()

    #show last window
    self.wn_previous.deiconify()
    self.wn_previous.lift()

  def next_window(self):
    #check if file is loadid
    if(self.isFileLoad):
      #Check if value are right
      if(not self.final_checks()):
        return

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Managing file...")
      
      #create thread to manage the file
      manage_file_thread = ManageTaxonomicDynamic(self)
      manage_file_thread.start()
      self.monitor_manage_file(manage_file_thread, "next_window")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_next_window(self):
    #Edit the previous dict
    MyUtility.workDict["taxonomic"] = True

    #hide this window
    self.withdraw()
    #create new window
    self.windowFunctionalMenu = wFnMn.FunctionalMenuWindow(self.wn_root, self, self.df_tmp)

  def skip_window(self):
    #Edit the previous dict
    MyUtility.workDict["taxonomic"] = False

    #hide this window
    self.withdraw()
    #create new window
    self.windowFunctionalMenu = wFnMn.FunctionalMenuWindow(self.wn_root, self, self.df)


'''
if __name__ == "__main__":
  app = TaxonomicWindow()
  app.mainloop()
'''