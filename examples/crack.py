class PresentationCrack:
    """Gives a presentation of Dogtail, using Dogtail itself."""

    def __init__(self):
        self.evo = EvolutionApp()
        self.pageNumber = 0
        self.pageDelay = 3

    def startPage(self, title):
        sleep (self.pageDelay)
        self.pageNumber+=1
        self.composer = self.evo.composeEmail()
        self.composer.subject = "Presentation page %s"%self.pageNumber

        self.composer.setHtml(True)

        self.composer.setHeader(1)
        self.composer.htmlNode.text = title
        self.composer.htmlNode.typeText("\n\n")

    def addBullet(self, text):
        self.composer.child("Bulleted List").click()
        self.composer.htmlNode.typeText(text)

    def runPresentation(self):
        self.startPage("Dogtail: a Free Automated GUI test tool")
        self.addBullet("foo")
        self.addBullet("bar")

        self.startPage("Leveraging Synergies")
        self.addBullet("pirates!")
        self.addBullet("zombies!")
        self.addBullet("zombie pirates!")

        self.startPage("4-Stroke Internal Combustion Engine")
        self.addBullet("suck")
        self.addBullet("squeeze")
        self.addBullet("bang")
        self.addBullet("blow")

        self.startPage("Questions?")

def runPresentationCrack():
    pres = PresentationCrack()
    pres.runPresentation()

runPresentationCrack()
