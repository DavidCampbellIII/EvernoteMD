import os
from xml.etree import ElementTree as ET
import html2text

class Converter:
    def __init__(self, rootDir, outDir):
        self.rootDir = rootDir
        self.outDir = outDir
        
        textMaker = html2text.HTML2Text()
        textMaker.unicode_snob = True
        textMaker.single_line_break = True
        textMaker.body_width = None
        textMaker.emphasis_mark = '*'
        self.textMaker = textMaker
        
    def run(self):
        if not os.path.exists(self.rootDir):
            print(f'Root directory "{self.rootDir}" does not exist!')
            return

        for f in os.listdir(self.rootDir):
            self.processFile(f)
            
    def processFile(self, file):
        subDir = self.createOutSubDirectory(file)
        print(subDir)
        
        filePath = os.path.join(self.rootDir, file)
        tree = ET.parse(filePath)
        root = tree.getroot()
        for note in root.findall(".//note"):
            self.parseAndWriteNote(note, subDir)
    
    def createOutSubDirectory(self, file):
        parts = file.split(".")[0].split("_")
        subDir = self.outDir + "/" + "/".join(parts)
        if not os.path.exists(subDir):
            os.makedirs(subDir)
        return subDir
    
    def parseAndWriteNote(self, note, outDir):
        result = self.getNoteTitle(note)
        title = result[0]
        
        time = None
        if len(result) > 1:
            time = result[1]
            
        tags = outDir.split("/")[1:]
        content = self.getNoteContent(note, tags, time)
        
        filePath = os.path.join(outDir, title)
        with open(filePath, "w", encoding="utf-8") as file:
            file.write(content)
        
    def getNoteTitle(self, note):
        noteTitle = note.find(".//title").text
        parts = noteTitle.split(" ")
        #result is [title, time(optional)]
        result = [""]
        for part in parts:
            if ":" not in part:
                result[0] += part + " "
            else:
                #time has a ":" in it
                result.append(part)
        result[0] = result[0].strip(", ") + ".md"
        return result
    
    def getNoteContent(self, note, tags, time):
        content = note.find(".//content").text
        
        text = "tags: " + " ".join(f'#{self.processTag(tag)}' for tag in tags)
        text += "\n\n---\n"
        text += self.textMaker.handle(content).strip()
        text = text.replace("  \n", "")
        
        if time:
            text += "\n\n" + time
        return text
    
    def processTag(self, tag):
        tag = tag.lower()
        if tag[0].isdigit():
            return f"Y_{tag}"
        return tag