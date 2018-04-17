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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 615,360 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_grid2 = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.m_grid2.CreateGrid( 10, 6 )
		self.m_grid2.EnableEditing( True )
		self.m_grid2.EnableGridLines( True )
		self.m_grid2.EnableDragGridSize( False )
		self.m_grid2.SetMargins( 0, 0 )
		
		# Columns
		self.m_grid2.EnableDragColMove( False )
		self.m_grid2.EnableDragColSize( True )
		self.m_grid2.SetColLabelSize( 30 )
		self.m_grid2.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.m_grid2.EnableDragRowSize( True )
		self.m_grid2.SetRowLabelSize( 80 )
		self.m_grid2.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.m_grid2.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer3.Add( self.m_grid2, 0, wx.ALL, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.m_staticText8.Wrap( -1 )
		bSizer5.Add( self.m_staticText8, 0, wx.ALL, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		self.m_staticText9.SetMinSize( wx.Size( 200,-1 ) )
		
		bSizer5.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		
		bSizer3.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button11 = wx.Button( self, wx.ID_ANY, u"加载词语", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button11, 0, wx.ALL, 5 )
		
		self.m_button12 = wx.Button( self, wx.ID_ANY, u"开始听写", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button12, 0, wx.ALL, 5 )
		
		self.m_button13 = wx.Button( self, wx.ID_ANY, u"下一个", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button13, 0, wx.ALL, 5 )
		
		self.m_button14 = wx.Button( self, wx.ID_ANY, u"暂停", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button14, 0, wx.ALL, 5 )
		
		self.m_button15 = wx.Button( self, wx.ID_ANY, u"帮助", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button15, 0, wx.ALL, 5 )
		
		
		bSizer3.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer3 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button11.Bind( wx.EVT_LEFT_UP, self.loadWords )
		self.m_button12.Bind( wx.EVT_LEFT_UP, self.start )
		self.m_button13.Bind( wx.EVT_LEFT_UP, self.nextword )
		self.m_button14.Bind( wx.EVT_LEFT_UP, self.pause )
		self.m_button15.Bind( wx.EVT_LEFT_UP, self.help )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def loadWords( self, event ):
		event.Skip()
	
	def start( self, event ):
		event.Skip()
	
	def nextword( self, event ):
		event.Skip()
	
	def pause( self, event ):
		event.Skip()
	
	def help( self, event ):
		event.Skip()
	

