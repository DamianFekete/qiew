import UnpackPlugin
from TextDecorators import *
from PyQt5 import QtGui, QtCore, QtWidgets
import PyQt5
import sys, os

import pyaes


class aes(UnpackPlugin.DecryptPlugin):
    priority = 0

    def init(self, dataModel, viewMode):
        super(aes, self).init(dataModel, viewMode)

        root = os.path.dirname(sys.argv[0])
        self.ui = PyQt5.uic.loadUi(os.path.join(root, 'plugins', 'unpack', 'aes.ui'))

        self.ui.op.activated[str].connect(self._itemchanged)
        self.ui.op_iv.activated[str].connect(self._itemchanged_iv)

        self.ui.key.textChanged[str].connect(self._textchanged_key)
        self.ui.iv.textChanged[str].connect(self._textchanged_iv)
        return True

    def _textchanged_key(self, text):
        self.ui.label_key.setStyleSheet("QLabel {color : black; }")
        return

    def _textchanged_iv(self, text):
        self.ui.label_iv.setStyleSheet("QLabel {color : black; }")
        return

    def getUI(self):
        return self.ui

    def _itemchanged_iv(self, text):
        text = str(text)

        if text == 'Hex':
            # hex validator
            self.ui.iv.setText('')
            self.ui.iv.setValidator(UnpackPlugin.MyValidator(self.ui.iv))
        else:
            # no validator for string
            self.ui.iv.setText('')
            self.ui.iv.setValidator(None)

    def _itemchanged(self, text):
        self.ui.label_key.setStyleSheet("QLabel {color : red; }")
        text = str(text)

        if text == 'Hex':
            # hex validator
    	    self.ui.key.setText('')
    	    self.ui.key.setValidator(UnpackPlugin.MyValidator(self.ui.key))
        else:
    	    # no validator for string
    	    self.ui.key.setText('')
    	    self.ui.key.setValidator(None)

    def _getvalue(self, op, key):

        if key == '':
            return bytes(key)

        if op == 'Hex':
            key = UnpackPlugin._convert(key)
            key = key.to_bytes((key.bit_length() + 7) // 8, byteorder='little')
        else:
            key = bytes(key, 'utf-8')

        return key

    def proceed(self):

        key = self._getvalue(str(self.ui.op.currentText()), str(self.ui.key.text()))
        iv = self._getvalue(str(self.ui.op_iv.currentText()), str(self.ui.iv.text()))
  
        if len(key) not in [16, 24, 32]:
            self.ui.label_key.setStyleSheet("QLabel {color : red; }")
            return False

        if len(iv) != 16:
            self.ui.label_iv.setStyleSheet("QLabel {color : red; }")
            return False

        aesop = str(self.ui.op_aes.currentText())

        if self.viewMode.selector.getCurrentSelection():
            u, v = self.viewMode.selector.getCurrentSelection()

            #aes = pyaes.AESModeOfOperationCFB(key, iv = iv, segment_size = 1)

            # we support only CBC now
            aes = pyaes.AESModeOfOperationCBC(key, iv)
            plaintext =  self.dataModel.getStream(u, v)

            # damn!
            blocks = len(plaintext)//16
            k = 0
            for i in range(blocks):
                block = [chr(c) for c in plaintext[k:k+16]]
                if aesop == 'encrypt':
                    ciphertext = aes.encrypt(block)
                else:
                    ciphertext = aes.decrypt(block)

                self.dataModel.setData_s(u+k, u+k+16, ciphertext)

                k += 16
                #0123456789abcdef
                #00 11 22 33 44 55 66 77 bb 99 aa bb cc dd ee ff

        return True
