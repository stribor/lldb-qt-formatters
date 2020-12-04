import lldb
import sys
import traceback

def __lldb_init_module(debugger, unused):
    # types created through the Python code
    debugger.HandleCommand('type summary add -x "^QUrl$" -e -F QtFormatters.QUrl_SummaryProvider')
    debugger.HandleCommand('type summary add -x "^QString$" -e -F QtFormatters.QString_SummaryProvider')
    debugger.HandleCommand('type synthetic add -x "^QVector<.+>$" -l QtFormatters.QVector_SyntheticProvider')
    debugger.HandleCommand('type summary add -x "^QVector<.+>$" -e -s "size=${svar%#}"')
    debugger.HandleCommand('type synthetic add -x "^QList<.+>$" -l QtFormatters.QList_SyntheticProvider')
    debugger.HandleCommand('type summary add -x "^QList<.+>$" -e -s "size=${svar%#}"')
    debugger.HandleCommand('type synthetic add -x "^QPointer<.+>$" -l QtFormatters.QPointer_SyntheticProvider')
    debugger.HandleCommand('type summary add -x "^QPointer<.+>$" -e -s "filled="${svar%#}"')
    debugger.HandleCommand('type synthetic add -x "^QVariant$" -l QtFormatters.QVariant_SyntheticProvider')
    debugger.HandleCommand('type summary add -x "^QVariant$" -e -s "${svar[0]%V}"')
    # summary only types 
    debugger.HandleCommand('type summary add --summary-string "(w=${var.wd}, h=${var.ht})" QSize')
    debugger.HandleCommand('type summary add --summary-string "(w=${var.wd}, h=${var.ht})" QSizeF')
    debugger.HandleCommand('type summary add --summary-string "(x=${var.xp}, y=${var.yp})" QPoint')
    debugger.HandleCommand('type summary add --summary-string "(x=${var.xp}, y=${var.yp})" QPointF')
    debugger.HandleCommand('type summary add --summary-string "(x1=${var.x1}, y1=${var.y1}), size=(w=${var.x2}, h=${var.y2})" QRect')
    debugger.HandleCommand('type summary add --summary-string "(xp=${var.xp}, yp=${var.yp}), size=(w=${var.w},h=${var.h})" QRectF')
    debugger.HandleCommand('type summary add --summary-string "\{${var.data1%x} - ${var.data2%x} - ${var.data3%x} - ${var.data4[0-7]%x}\}" QUuid')    


def printException():
    eInfo = sys.exc_info()
    print ("Exception:")
    print (traceback.print_tb(eInfo[2], 1))
    print (eInfo[0], eInfo[1] )
    return

def QString_SummaryProvider(valobj, internal_dict):
   def make_string_from_pointer_with_offset(F,OFFS,L):
       strval = '"'
       try:
           data_array = F.GetPointeeData(0, L).uint16
           for X in range(OFFS, L):
               V = data_array[X]
               if V == 0:
                   break
               strval += chr(V)
       # Ignore index error because if you set breakpoint on a line that constructs a QString
       # it has not yet been defined and you end up with an IndexError unable to read data_array
       except(IndexError):
           pass
       except:
           printException()
           pass
       strval = strval + '"'
       return strval

   #qt5
   def qstring_summary(value):
       try:
           d = value.GetChildMemberWithName('d')
           #have to divide by 2 (size of unsigned short = 2)
           offset = d.GetChildMemberWithName('offset').GetValueAsUnsigned() // 2
           size = get_max_size(value)
           return make_string_from_pointer_with_offset(d, offset, size)
       except:
           printException()
           return value

   def get_max_size(value):
       _max_size_ = None
       try:
           debugger = value.GetTarget().GetDebugger()
           _max_size_ = int(lldb.SBDebugger.GetInternalVariableValue('target.max-string-summary-length', debugger.GetInstanceName()).GetStringAtIndex(0))
       except:
           _max_size_ = 512
       return _max_size_
   return qstring_summary(valobj)

def QUrl_SummaryProvider(valobj, internal_dict):
   return QString_SummaryProvider(valobj.GetFrame().EvaluateExpression(valobj.GetName() + '.toString(QUrl::ComponentFormattingOption::PrettyDecoded)'), None)

class QVector_SyntheticProvider:
    def __init__(self, valobj, internal_dict):
            self.valobj = valobj

    def num_children(self):
            try:
                    s = self.valobj.GetChildMemberWithName('d').GetChildMemberWithName('size').GetValueAsUnsigned()
                    return s
            except:
                    return 0

    def get_child_index(self,name):
            try:
                    return int(name.lstrip('[').rstrip(']'))
            except:
                    return None

    def get_child_at_index(self,index):
            if index < 0:
                    return None
            if index >= self.num_children():
                    return None
            if self.valobj.IsValid() == False:
                    return None
            try:
                    doffset = self.valobj.GetChildMemberWithName('d').GetChildMemberWithName('offset').GetValueAsUnsigned()
                    type = self.valobj.GetType().GetTemplateArgumentType(0)
                    elementSize = type.GetByteSize()
                    return self.valobj.GetChildMemberWithName('d').CreateChildAtOffset('[' + str(index) + ']', doffset + index * elementSize, type)
            except:
                    return None

class QList_SyntheticProvider:
    def __init__(self, valobj, internal_dict):
            self.valobj = valobj

    def num_children(self):
            try:
                    listDataD = self.valobj.GetChildMemberWithName('p').GetChildMemberWithName('d')
                    begin = listDataD.GetChildMemberWithName('begin').GetValueAsUnsigned()
                    end = listDataD.GetChildMemberWithName('end').GetValueAsUnsigned()
                    return (end - begin)
            except:
                    return 0

    def get_child_index(self,name):
            try:
                    return int(name.lstrip('[').rstrip(']'))
            except:
                    return None

    def get_child_at_index(self,index):
            if index < 0:
                    return None
            if index >= self.num_children():
                    return None
            if self.valobj.IsValid() == False:
                    return None
            try:
                    pD = self.valobj.GetChildMemberWithName('p').GetChildMemberWithName('d')
                    pBegin = pD.GetChildMemberWithName('begin').GetValueAsUnsigned()
                    argType = self.valobj.GetType().GetTemplateArgumentType(0)
                    voidSize = pD.GetChildMemberWithName('array').GetType().GetByteSize()
                    return self.valobj.GetChildMemberWithName('p').GetChildMemberWithName('d').GetChildMemberWithName('array').CreateChildAtOffset('[' + str(index) + ']', pBegin + index * voidSize, argType)
            except:
                    printException()
                    return None

class QPointer_SyntheticProvider:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj

    def num_children(self):
        try:
            wp = self.valobj.GetChildMemberWithName('wp')
            d = wp.GetChildMemberWithName('d')
            if d.GetValueAsUnsigned() == 0 or d.GetChildMemberWithName('strongref').GetChildMemberWithName('_q_value').GetValueAsUnsigned() == 0 or wp.GetChildMemberWithName('value').GetValueAsUnsigned() == 0:
                return 0
            else:
                return 1
        except:
            return 0

    def get_child_index(self,name):
        return 0

    def get_child_at_index(self,index):
        if index < 0:
            return None
        if index >= self.num_children():
            return None
        if self.valobj.IsValid() == False:
            return None
        try:
            type = self.valobj.GetType().GetTemplateArgumentType(0)
            return self.valobj.GetChildMemberWithName('wp').GetChildMemberWithName('value').CreateChildAtOffset('value', 0, type)
        except:
            printException()
            return None

class QVariant_SyntheticProvider:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj

    def num_children(self):
        return 1

    def get_child_index(self,name):
        return 0

    def get_child_at_index(self,index):
        if index != 0:
            return None
        if self.valobj.IsValid() == False:
            return None

        target = lldb.debugger.GetSelectedTarget()
        variantType = self.valobj.GetChildMemberWithName('d').GetChildMemberWithName('type').GetValueAsUnsigned()
        dMember = self.valobj.GetChildMemberWithName('d')
        resultType = None

        if variantType == 1:
            value = dMember.GetChildMemberWithName('data').GetChildMemberWithName('b')
        elif variantType == 2:
            value = dMember.GetChildMemberWithName('data').GetChildMemberWithName('i')
        elif variantType == 3:
            value = dMember.GetChildMemberWithName('data').GetChildMemberWithName('u')
        elif variantType == 4:
            value = dMember.GetChildMemberWithName('data').GetChildMemberWithName('ll')
        elif variantType == 5:
            value = dMember.GetChildMemberWithName('data').GetChildMemberWithName('ull')
        elif variantType == 6:
            value = dMember.GetChildMemberWithName('data').GetChildMemberWithName('d')
        elif variantType == 7:
            value = dMember.GetChildMemberWithName('data').GetChildMemberWithName('c')
        elif variantType == 8:
            resultType = target.FindFirstType('QVariantMap')
        elif variantType == 9:
            resultType = target.FindFirstType('QVariantList')
        elif variantType == 10:
            resultType = target.FindFirstType('QString')
        elif variantType == 11:
            resultType = target.FindFirstType('QStringList')
        elif variantType == 12:
            resultType = target.FindFirstType('QByteArray')
        elif variantType == 13:
            resultType = target.FindFirstType('QBitArray')
        elif variantType == 14:
            resultType = target.FindFirstType('QDate')
        elif variantType == 15:
            resultType = target.FindFirstType('QTime')
        elif variantType == 16:
            resultType = target.FindFirstType('QDateTime')
        elif variantType == 17:
            resultType = target.FindFirstType('QUrl')
        elif variantType == 18:
            resultType = target.FindFirstType('QLocale')
        elif variantType == 19:
            resultType = target.FindFirstType('QRect')
        elif variantType == 20:
            resultType = target.FindFirstType('QRectF')
        elif variantType == 21:
            resultType = target.FindFirstType('QSize')
        elif variantType == 22:
            resultType = target.FindFirstType('QSizeF')
        elif variantType == 23:
            resultType = target.FindFirstType('QLine')
        elif variantType == 24:
            resultType = target.FindFirstType('QLineF')
        elif variantType == 25:
            resultType = target.FindFirstType('QPoint')
        elif variantType == 26:
            resultType = target.FindFirstType('QPointF')
        elif variantType == 27:
            resultType = target.FindFirstType('QRegExp')
        elif variantType == 28:
            resultType = target.FindFirstType('QVariantHash')
        elif variantType == 29:
            resultType = target.FindFirstType('QEasingCurve')
        elif variantType == 30:
            resultType = target.FindFirstType('QUuid')
        elif variantType == 42:
            resultType = target.FindFirstType('QModelIndex')
        elif variantType == 44:
            resultType = target.FindFirstType('QRegularExpression')
        elif variantType == 50:
            resultType = target.FindFirstType('QPersistentModelIndex')
        elif variantType == 64:
            resultType = target.FindFirstType('QFont')
        elif variantType == 65:
            resultType = target.FindFirstType('QPixmap')
        elif variantType == 66:
            resultType = target.FindFirstType('QBrush')
        elif variantType == 67:
            resultType = target.FindFirstType('QColor')
        elif variantType == 68:
            resultType = target.FindFirstType('QPalette')
        elif variantType == 69:
            resultType = target.FindFirstType('QIcon')
        elif variantType == 70:
            resultType = target.FindFirstType('QImage')
        elif variantType == 71:
            resultType = target.FindFirstType('QPolygon')
        elif variantType == 72:
            resultType = target.FindFirstType('QRegion')
        elif variantType == 73:
            resultType = target.FindFirstType('QBitmap')
        elif variantType == 74:
            resultType = target.FindFirstType('QCursor')
        elif variantType == 75:
            resultType = target.FindFirstType('QKeySequence')
        elif variantType == 76:
            resultType = target.FindFirstType('QPen')
        elif variantType == 77:
            resultType = target.FindFirstType('QTextLength')
        elif variantType == 78:
            resultType = target.FindFirstType('QTextFormat')
        elif variantType == 79:
            resultType = target.FindFirstType('QMatrix')
        elif variantType == 80:
            resultType = target.FindFirstType('QTransform')
        elif variantType == 81:
            resultType = target.FindFirstType('QMatrix4x4')
        elif variantType == 82:
            resultType = target.FindFirstType('QVector2D')
        elif variantType == 83:
            resultType = target.FindFirstType('QVector3D')
        elif variantType == 84:
            resultType = target.FindFirstType('QVector4D')
        elif variantType == 85:
            resultType = target.FindFirstType('QQuaternion')
        elif variantType == 86:
            resultType = target.FindFirstType('QPolygonF')
        elif variantType == 121:
            resultType = target.FindFirstType('QSizePolicy')
        else:
            return dMember.GetChildMemberWithName('type')

        if resultType == None:
            resultType = value.GetType()
        else:
            value = dMember

        return value.CreateChildAtOffset('value', 0, resultType)
