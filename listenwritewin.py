# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"词语听写", pos = wx.DefaultPosition, size = wx.Size( 1150,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetFont( wx.Font( 20, 70, 90, 90, False, "宋体" ) )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_grid2 = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 1120,400 ), wx.VSCROLL )
		
		# Grid
		self.m_grid2.CreateGrid( 20, 6 )
		self.m_grid2.EnableEditing( False )
		self.m_grid2.EnableGridLines( True )
		self.m_grid2.SetGridLineColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )
		self.m_grid2.EnableDragGridSize( False )
		self.m_grid2.SetMargins( 0, 0 )
		
		# Columns
		self.m_grid2.SetColSize( 0, 180 )
		self.m_grid2.SetColSize( 1, 180 )
		self.m_grid2.SetColSize( 2, 180 )
		self.m_grid2.SetColSize( 3, 180 )
		self.m_grid2.SetColSize( 4, 180 )
		self.m_grid2.SetColSize( 5, 180 )
		self.m_grid2.EnableDragColMove( False )
		self.m_grid2.EnableDragColSize( True )
		self.m_grid2.SetColLabelSize( 30 )
		self.m_grid2.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.m_grid2.SetRowSize( 0, 35 )
		self.m_grid2.SetRowSize( 1, 35 )
		self.m_grid2.SetRowSize( 2, 35 )
		self.m_grid2.SetRowSize( 3, 35 )
		self.m_grid2.SetRowSize( 4, 35 )
		self.m_grid2.SetRowSize( 5, 35 )
		self.m_grid2.SetRowSize( 6, 35 )
		self.m_grid2.SetRowSize( 7, 35 )
		self.m_grid2.SetRowSize( 8, 35 )
		self.m_grid2.SetRowSize( 9, 35 )
		self.m_grid2.EnableDragRowSize( True )
		self.m_grid2.SetRowLabelSize( 30 )
		self.m_grid2.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.m_grid2.SetDefaultCellAlignment( wx.ALIGN_CENTRE, wx.ALIGN_TOP )
		self.m_grid2.SetFont( wx.Font( 20, 70, 90, 90, False, "宋体" ) )
		
		bSizer3.Add( self.m_grid2, 0, wx.ALL, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"拼音", wx.Point( 100,-1 ), wx.Size( 300,-1 ), 0 )
		self.m_staticText8.Wrap( -1 )
		bSizer5.Add( self.m_staticText8, 0, wx.ALL, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"词语", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		self.m_staticText9.SetMinSize( wx.Size( 200,-1 ) )
		
		bSizer5.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		
		bSizer3.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button11 = wx.Button( self, wx.ID_ANY, u"显示词语", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button11.SetFont( wx.Font( 20, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer6.Add( self.m_button11, 0, wx.ALL, 5 )
		
		self.m_button12 = wx.Button( self, wx.ID_ANY, u"开始听写", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button12, 0, wx.ALL, 5 )
		
		self.m_button13 = wx.Button( self, wx.ID_ANY, u"下一个", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button13, 0, wx.ALL, 5 )
		
		self.m_button14 = wx.Button( self, wx.ID_ANY, u"暂停", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button14, 0, wx.ALL, 5 )
		
		self.m_button15 = wx.Button( self, wx.ID_ANY, u"继续", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button15, 0, wx.ALL, 5 )
		
		self.m_button6 = wx.Button( self, wx.ID_ANY, u"记录结果", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button6, 0, wx.ALL, 5 )
		
		self.m_button8 = wx.Button( self, wx.ID_ANY, u"保存错词", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button8, 0, wx.ALL, 5 )
		
		
		bSizer3.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer3 )
		self.Layout()
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menubar1.SetFont( wx.Font( 20, 70, 90, 90, False, wx.EmptyString ) )
		
		self.m_menu1 = wx.Menu()
		self.m_menuItem1 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"导入词语", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.Append( self.m_menuItem1 )
		
		self.m_menubar1.Append( self.m_menu1, u"文件" ) 
		
		self.m_menu2 = wx.Menu()
		self.m_menuItem2 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"生词", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.Append( self.m_menuItem2 )
		
		self.m_menuItem3 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"错词", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.Append( self.m_menuItem3 )
		
		self.m_menubar1.Append( self.m_menu2, u"词语" ) 
		
		self.m_menu3 = wx.Menu()
		self.m_menubar1.Append( self.m_menu3, u"选项" ) 
		
		self.m_menu4 = wx.Menu()
		self.m_menuItem4 = wx.MenuItem( self.m_menu4, wx.ID_ANY, u"帮助", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu4.Append( self.m_menuItem4 )
		
		self.m_menubar1.Append( self.m_menu4, u"帮助" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		
		# Connect Events
		self.m_grid2.Bind( wx.grid.EVT_GRID_RANGE_SELECT, self.onRangeSelect )
		self.m_grid2.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.selectCell )
		self.m_button11.Bind( wx.EVT_BUTTON, self.displayWords )
		self.m_button12.Bind( wx.EVT_BUTTON, self.startListen )
		self.m_button13.Bind( wx.EVT_BUTTON, self.nextWord )
		self.m_button14.Bind( wx.EVT_BUTTON, self.pause )
		self.m_button15.Bind( wx.EVT_BUTTON, self.playContinue )
		self.m_button6.Bind( wx.EVT_BUTTON, self.saveTest )
		self.m_button8.Bind( wx.EVT_BUTTON, self.saveError )
		self.Bind( wx.EVT_MENU, self.importWords, id = self.m_menuItem1.GetId() )
		self.Bind( wx.EVT_MENU, self.listenNew, id = self.m_menuItem2.GetId() )
		self.Bind( wx.EVT_MENU, self.listenWrong, id = self.m_menuItem3.GetId() )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onRangeSelect( self, event ):
		event.Skip()
	
	def selectCell( self, event ):
		event.Skip()
	
	def displayWords( self, event ):
		event.Skip()
	
	def startListen( self, event ):
		event.Skip()
	
	def nextWord( self, event ):
		event.Skip()
	
	def pause( self, event ):
		event.Skip()
	
	def playContinue( self, event ):
		event.Skip()
	
	def saveTest( self, event ):
		event.Skip()
	
	def saveError( self, event ):
		event.Skip()
	
	def importWords( self, event ):
		event.Skip()
	
	def listenNew( self, event ):
		event.Skip()
	
	def listenWrong( self, event ):
		event.Skip()
	

###########################################################################
## Class MyDialog1
###########################################################################

class MyDialog1 ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 488,330 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer3.SetFlexibleDirection( wx.BOTH )
		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"出版社", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		fgSizer3.Add( self.m_staticText7, 0, wx.ALL, 5 )
		
		m_choice5Choices = []
		self.m_choice5 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice5Choices, 0 )
		self.m_choice5.SetSelection( 0 )
		fgSizer3.Add( self.m_choice5, 0, wx.ALL, 5 )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"课本", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		fgSizer3.Add( self.m_staticText8, 0, wx.ALL, 5 )
		
		m_choice6Choices = []
		self.m_choice6 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice6Choices, 0 )
		self.m_choice6.SetSelection( 0 )
		fgSizer3.Add( self.m_choice6, 0, wx.ALL, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"单元", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer3.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		m_choice7Choices = []
		self.m_choice7 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice7Choices, 0 )
		self.m_choice7.SetSelection( 0 )
		fgSizer3.Add( self.m_choice7, 0, wx.ALL, 5 )
		
		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"课文", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		fgSizer3.Add( self.m_staticText10, 0, wx.ALL, 5 )
		
		m_choice8Choices = []
		self.m_choice8 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice8Choices, 0 )
		self.m_choice8.SetSelection( 0 )
		fgSizer3.Add( self.m_choice8, 0, wx.ALL, 5 )
		
		self.m_staticText81 = wx.StaticText( self, wx.ID_ANY, u"时间", wx.Point( 1,5 ), wx.DefaultSize, 0 )
		self.m_staticText81.Wrap( -1 )
		fgSizer3.Add( self.m_staticText81, 0, wx.ALL, 5 )
		
		m_choice71Choices = []
		self.m_choice71 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice71Choices, 0 )
		self.m_choice71.SetSelection( 0 )
		fgSizer3.Add( self.m_choice71, 0, wx.ALL, 5 )
		
		self.m_staticText101 = wx.StaticText( self, wx.ID_ANY, u"测试", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText101.Wrap( -1 )
		fgSizer3.Add( self.m_staticText101, 0, wx.ALL, 5 )
		
		m_choice81Choices = []
		self.m_choice81 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice81Choices, 0 )
		self.m_choice81.SetSelection( 0 )
		fgSizer3.Add( self.m_choice81, 0, wx.ALL, 5 )
		
		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"词语", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		fgSizer3.Add( self.m_staticText11, 0, wx.ALL, 5 )
		
		m_choice9Choices = []
		self.m_choice9 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice9Choices, 0 )
		self.m_choice9.SetSelection( 0 )
		fgSizer3.Add( self.m_choice9, 0, wx.ALL, 5 )
		
		self.m_button9 = wx.Button( self, wx.ID_ANY, u"确定", wx.Point( 1,8 ), wx.DefaultSize, 0 )
		fgSizer3.Add( self.m_button9, 0, wx.ALL, 5 )
		
		
		self.SetSizer( fgSizer3 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_choice5.Bind( wx.EVT_CHOICE, self.pressSelect )
		self.m_choice6.Bind( wx.EVT_CHOICE, self.bookSelect )
		self.m_choice7.Bind( wx.EVT_CHOICE, self.unitSelect )
		self.m_choice8.Bind( wx.EVT_CHOICE, self.lessonSelect )
		self.m_choice81.Bind( wx.EVT_CHOICE, self.testSelect )
		self.m_button9.Bind( wx.EVT_BUTTON, self.DoOk )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def pressSelect( self, event ):
		event.Skip()
	
	def bookSelect( self, event ):
		event.Skip()
	
	def unitSelect( self, event ):
		event.Skip()
	
	def lessonSelect( self, event ):
		event.Skip()
	
	def testSelect( self, event ):
		event.Skip()
	
	def DoOk( self, event ):
		event.Skip()
	

