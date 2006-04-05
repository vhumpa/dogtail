import dogtail.tree

class Gedit(dogtail.tree.Application):
    def setText(self, text):
        buf = self.child(roleName = 'text')
        buf.text = text

    def getText(self):
        return self.child(roleName='text').text

    def openLocation(self, uri):
        menuItem = self.menu("File").menuItem("Open Location...")
        menuItem.click()
        dlg = self.dialog('Open Location')
        dlg.child(roleName = 'text').text = uri
        dlg.button('Open').click()

    def saveAs(self, uri):
        menuItem = self.menu("File").menuItem("Save As...")
        menuItem.click()
        dlg = self.dialog('Save As...')
        dlg.child(roleName = 'text').text = uri
        dlg.button('Save').click()

    def printPreview(self):
        menuItem = self.menu("File").menuItem("Print Preview")
        menuItem.click()
