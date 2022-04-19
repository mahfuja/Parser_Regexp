#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:17:17 2020
Version 1.1

@author: akter
"""
import re
import sys
import argparse

class UtransLogParser:
    def __init__(self, args):
        self.logfile = args.infile
        self.outfile = args.outfile
        self.columns = ['log step', 'description', 'status', 'iterations', 'armijo', 'NLP residual', 'newton']
        self.DAESolver = False
        if "DAESolver" in args.list:
            self.DAEcolumns = ['step','time', 'iterations', 'armijo', 'NLP residual', 'total time']
            self.DAESolver = True
        else:
            if args.list:
                self.columns += [item for item in args.list.split(',')]
            else:
                self.columns += ['utrans', 'postNL']
            self.columns += ['read', 'write']

        if not self.DAESolver:
            self.outfile.write(",".join(str(x) for x in self.columns))
            self.outfile.write("\n")
        self.stepCount = 0
        self.colData = {}
        self.timeSums = {}
        self.timeSums["description"] = "sum"
        self.timeSums["iterations"] = 0
        self.timeSums["armijo"] = 0
        self.timeSums["newton"] = 0.0
        self.timeSums["read"] = 0.0
        self.timeSums["write"] = 0.0
        self.timeSums["NLP residual"] = 0.0
        self.timeSums["total time"] = 0.0

    def readNextStep(self, line):
        description = re.search("=============(.*)===============", line)
        if description:
            if self.step != "":
                self.colData["log step"] = str(self.stepCount)
                vals = [self.colData.get(x, "") for x in self.columns]
                self.outfile.write(",".join(vals) + "\n")
                self.stepCount = self.stepCount+1
            self.step = description.group(1).strip()
            self.section = ""
            self.colData = {}
            self.colData["description"] = str(self.step)
            self.colData["status"] = "0"
            return True
        return False

    def readNextSection(self, line):
        section = re.search("-------------(.*) ---------------", line)
        if section:
            section = section.group(1).strip()
            self.section = section
            if self.timeSums.get(self.section) is None:
                self.timeSums[self.section] = float(0)
            return True
        return False

    def timeSigOfSection(self):
        timeSignatures = {
            'utrans': '^translate: (.*)',
            'postNL': '^filter: (.*)',
            'mix-g' : '^mix: (.*)'
        }
        return timeSignatures.get(self.section, 'process: (.*)')

    def readTimings(self, line):
        time = re.search(self.timeSigOfSection(), line)
        if time:
            self.colData[self.section] = "%.3f" % float(time.group(1).split(' ')[0])
            self.timeSums[self.section] += float(self.colData[self.section])
            return True

        readTime = re.search("^read.*: (.*)", line)
        if readTime:
            f_read = float(readTime.group(1).split(' ')[0])
            self.colData["read"] = "%.3f" % (float(self.colData.get("read", "0")) + f_read)
            self.timeSums["read"] += f_read
            return True

        writeTime = re.search("^write.*: (.*)", line)
        if writeTime:
            f_write = float(writeTime.group(1).split(' ')[0])
            self.colData["write"] = "%.3f" % (float(self.colData.get("write", "0")) + f_write)
            self.timeSums["write"] += f_write
            return True

        return False

    def readNewtonSection(self, line):
        NLPresidual = re.search("\|f0\|=(.*)", line)
        if NLPresidual:
            self.colData["NLP residual"] = NLPresidual.group(1).split(' ')[0]
            return
        string = re.search("Solution found after (.*) iterations and (.*) total armijo steps", line)
        if string:
            self.colData["iterations"] = string.group(1).split(' ')[0]
            self.colData["armijo"] = string.group(2).split(' ')[0]
            self.timeSums["iterations"] += int(self.colData["iterations"])
            self.timeSums["armijo"] += int(self.colData["armijo"])
            return
        string = re.search("No solution after (.*) iterations and (.*) total armijo steps!", line)
        if string:
            self.colData["iterations"] = string.group(1).split(' ')[0]
            self.colData["armijo"] = string.group(2).split(' ')[0]
            self.colData["status"] = "-1"
            return
        timeNewton = re.search("time_newton: (.*)", line)
        if timeNewton:
            self.colData["newton"] = "%.3f" % float(timeNewton.group(1).split(' ')[0])
            self.timeSums["newton"] += float(self.colData["newton"])

    def readDAEFast(self, file):
        regDAE = "Implicit Euler Step .* \[t=(.*)\][\s\S]*?\|f0\|=(.*)  max=.* \n.*\nSolution found after (.*) iterations and (.*) total"
        contents = file.read()
        match = re.findall(regDAE,contents, re.M)
        if match:
            self.outfile.write(",".join(self.DAEcolumns) + "\n")
            for i in range(0,len(match)):
                self.stepCount += 1
                self.colData["step"] = str(i+1)
                self.colData["time"] = match[i][0]
                self.colData["iterations"] = "%d" % int(match[i][2])
                self.colData["armijo"] = "%d" % int(match[i][3])
                self.colData["NLP residual"] = match[i][1]
                self.timeSums["iterations"] += int(self.colData["iterations"])
                self.timeSums["NLP residual"] += float(self.colData["NLP residual"])
                self.timeSums["armijo"] += int(self.colData["armijo"])
                if self.stepCount < 100 or self.stepCount == len(match):
                    vals = [self.colData.get(x, "") for x in self.DAEcolumns]
                    self.outfile.write(",".join(vals) + "\n")
                elif self.stepCount == 100:
                    self.outfile.write("...,,,,,\n")
                else:
                    continue

        nosolv = re.findall("No solution after (.*) iterations and (.*) total armijo steps!",contents, re.M)
        if nosolv:
            self.colData["iterations"] = "%d" % int(nosolv[0][0])
            self.colData["armijo"] = "%d" % int(nosolv[0][1])
            vals = [self.colData.get(x, "") for x in self.DAEcolumns]
            self.outfile.write(",".join(vals) + "\n")
        timeDAESolver = re.findall("---- Implicit Euler End [\s\S]*?time:  (.*)",contents,re.M)
        if timeDAESolver:
            self.timeSums["total time"] = float(timeDAESolver[0])

    def parse(self):
        self.step = ""
        self.section = ""
        header = True;
        if self.DAESolver:
            self.readDAEFast(self.logfile)
            self.timeSums["step"] = "sum"
            self.timeSums["NLP residual"] = round(self.timeSums.get("NLP residual"),6)
            vals = [str(self.timeSums.get(x, "")) for x in self.DAEcolumns]
            self.outfile.write(",".join(vals) + "\n")
            self.outfile.write("total newton iterations: " +  str(self.timeSums["iterations"])+"\n")
            self.outfile.write("total armijo iterations:  "+ str(self.timeSums["armijo"])+"\n")
            self.outfile.write("total solver time: "+ str(self.timeSums.get("total time"))+"\n")
            self.outfile.write("time per solve step: " + str(self.timeSums.get("total time")/self.stepCount))
        else:
            contents = self.logfile.readlines()
            for line in contents:
                # rows of the output table (workflow steps: init, free, adv, mix, ...)
                if self.readNextStep(line):
                    continue
                # sections will appear as columns in output table
                if self.readNextSection(line):
                    continue
                if self.readTimings(line):
                    continue
                if self.section == "newton":
                    self.readNewtonSection(line)

            if self.step != "" and self.DAESolver == False:
                self.colData["log step"] = str(self.stepCount)
                vals = [self.colData.get(x, "") for x in self.columns]
                self.outfile.write(",".join(vals) + "\n")

                vals = [str(self.timeSums.get(x, "")) for x in self.columns]
                self.outfile.write(",".join(vals) + "\n")

            self.outfile.close()
            self.logfile.close()


argParser = argparse.ArgumentParser()
argParser.add_argument('-l', '--list', help='delimited list input', type=str)
argParser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
argParser.add_argument('outfile', nargs='?', type=argparse.FileType('w+'), default=sys.stdout)
args = argParser.parse_args()

ulp = UtransLogParser(args)
ulp.parse()
