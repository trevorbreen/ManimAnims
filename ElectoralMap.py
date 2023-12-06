from manim import *

class NewAnim(Scene):
    def construct(self):

        def move_votes(map,sourceId,targetId, n_votes=1):                
            source,target = map.votes[sourceId], map.votes[targetId]
            target_center = target.get_center()
            anims = []
            for _ in range(n_votes):
                map.voteCounts[sourceId] -= 1
                map.voteCounts[targetId] += 1
                popped = source.submobjects[-1]
                source -= popped
                target += popped
                rows = len(target.submobjects) // map.voteCols + 3

                anims += [target
                            .animate
                            .arrange_in_grid(rows=rows, cols=map.voteCols,buff=map.voteBuff)
                            .move_to(target_center)]
                anims += [Transform(map.winners[i],map.updateRidingWinner(i).copy())
                                    for i in range(map.ridingCount)]
                anims += [Transform(map.result,map.updateOverallWinner())]        
            return anims

        def swap_votes(map, sourceCol,targetCol, sourceRow,targetRow, n_votes=1):
            anims = []
            sourceId1 = sourceCol + (map.ridingCount * sourceRow)
            sourceId2 = targetCol + (map.ridingCount * targetRow)
            targetId1 = targetCol + (map.ridingCount * sourceRow)
            targetId2 = sourceCol + (map.ridingCount * targetRow)
            
            anims += map.move_votes(sourceId1, targetId1, n_votes)
            anims += map.move_votes(sourceId2, targetId2, n_votes)
            return anims
        
        def cut_to_text(duration,displayTextlist):
            content = self.mobjects
            textSegments = VGroup(*[Text(words) for words in displayTextlist]).arrange_in_grid(rows=len(displayTextlist))
            print(textSegments)

            self.play(FadeOut(*content))
            self.play(FadeIn(*textSegments))
            self.play(Wait(duration=duration))
            self.play(FadeOut(*textSegments))
            self.play(FadeIn(*content))

        def one_to_many(map, sourceId, targetIdList, n_votes=1):
            anims = []
            for targetId in targetIdList:
                anims += move_votes(map,sourceId,targetId,n_votes) 
            return anims
        def many_to_many(map, sourceIdList, targetIdList, n_votes=1):
            anims = []
            for sourceId in sourceIdList:
                for targetId in targetIdList:
                    anims += move_votes(map,sourceId,targetId,n_votes) 
            return anims
            
    
        class ElectoralMap:
            def __init__(self,voteArray,
                        voteBuff=0.05,voteRad=0.075,voteRows=6,
                        voteCols=5, gridBuff=0, cellHeight=1.2,
                        cellWidth=1.35,colors=[YELLOW,GREEN,PINK,WHITE],
                        ridingString="ABCDEFG", partyCount=3):
                
                self.voteBuff, self.voteRad = voteBuff, voteRad
                self.voteRows, self.voteCols = voteRows, voteCols
                self.gridBuff, self.cellHeight, self.cellWidth= gridBuff, cellHeight, cellWidth
                self.colors, self.voteArray = colors, voteArray

                self.partyCount, self.ridingCount = partyCount, len(ridingString)

                self.grid = (VGroup(*[Rectangle(height=cellHeight,width=cellWidth) for _ in range(self.partyCount*self.ridingCount)])
                                    .arrange_in_grid(rows=self.partyCount, cols=self.ridingCount,buff=gridBuff))
                self.shareGrid = (VGroup(*[Rectangle(height=cellHeight,width=cellWidth) for _ in range(self.partyCount)])
                                    .arrange_in_grid(rows=self.partyCount, cols=1,buff=gridBuff)
                                    .next_to(self.grid,RIGHT))
                self.winnerGrid = (VGroup(*[Rectangle(height=cellHeight,width=cellWidth) for _ in range(self.ridingCount)])
                                    .arrange_in_grid(rows=1, cols=self.ridingCount,buff=gridBuff)
                                    .next_to(self.grid,DOWN))
                
                self.ridingLabels = [Text(x).next_to(self.grid[i],UP) for i, x in enumerate(ridingString)]
                self.partyLabels = [(Star(color=colors[0], outer_radius=0.5, **{"fill_color":colors[0],"fill_opacity":0.75})
                                    .next_to(self.grid[0 * self.ridingCount],LEFT)),
                                    (Circle(color=colors[1],radius=0.45, **{"fill_color":colors[1],"fill_opacity":0.75})
                                    .next_to(self.grid[1 * self.ridingCount],LEFT)),
                                    (Triangle(color=colors[2],**{"radius":0.6,"fill_color":colors[2],"fill_opacity":0.75})
                                    .next_to(self.grid[2 * self.ridingCount],LEFT))]
                
                self.shareLabel = VGroup(*[Text("% of"),Text("Vote")]).arrange_in_grid(rows=2, cols=1).next_to(self.shareGrid,UP)
                self.partyTitle = Text("Party")
                
                self.winnerLabel = Text("Winner").next_to(self.winnerGrid,LEFT)
                self.ridingLabel = Text("Riding").next_to(VGroup(*self.ridingLabels),UP)
                self.votes = [VGroup(*[Circle(radius=self.voteRad,fill_opacity=1,color=(self.colors[i//self.ridingCount])) 
                                    for _ in range(self.voteArray[i])])
                                    .arrange_in_grid(rows=self.voteRows, cols=self.voteCols,buff=self.voteBuff)
                                    .move_to(cell.get_center())
                                    for i, cell in enumerate(self.grid)]
                
                self.winners = [self.updateRidingWinner(i).shift(DOWN * 0.4) for i in range(self.ridingCount)]
                
                self.resultLabel = Text("Result:").next_to(self.winnerGrid,DOWN).shift(LEFT * 3)
                self.result = self.updateOverallWinner().next_to(self.winnerGrid,DOWN).shift(UP * 0.15 + RIGHT * 0.15)              
                
                self.ridingWinnerTracker = [ValueTracker(-1) for _ in range(self.ridingCount)]
                self.voteShareObjects =  [DecimalNumber(self.partyVoteShares(i),0, mob_class=Text)
                                            .move_to(cell.get_center())
                                            for i, cell in enumerate(self.shareGrid)]

                for i, vote in enumerate(self.votes):
                    vote.add_updater(lambda x, i=i: self.ridingWinnerTracker[i % self.ridingCount].set_value(self.ridingWinners[i % self.ridingCount]))
                    vote.add_updater(lambda x, i=i: self.voteShareObjects[i // self.ridingCount].set_value(self.partyVoteShares(i // self.ridingCount)))
                self.partyTitle.next_to(self.partyLabels[0],UP*2)
                self.partyTitleUnderline = Underline(self.partyTitle)
            
            @property
            def voteCounts(self):
                return [len(partySupporters.submobjects) for partySupporters in self.votes]

            @property
            def ridingWinners(self):
                winners = []
                for i in range(self.ridingCount):
                    ridingVoters = [self.voteCounts[i + j * self.ridingCount] for j in range(self.partyCount)]
                    winningParty = [i for i, partyVoters in enumerate(ridingVoters) if partyVoters == max(ridingVoters)]
                    winners.append(winningParty[0] if len(winningParty) == 1 else self.partyCount)
                return winners

            @property
            def seatsWon(self):
                return [self.ridingWinners.count(i) for i in range(self.partyCount)]

            @property
            def largestParty(self): 
                return [i for i, j in enumerate(self.seatsWon) if j == max(self.seatsWon)]

            @property     
            def resultType(self):
                if len(self.largestParty) > 1:
                    return Text("Tie").copy()
                else:
                    return (Text("Majority",weight=BOLD).copy()
                                if (max(self.seatsWon)/sum(self.seatsWon)) >= 0.5 else
                                Text("Minority",slant=ITALIC).copy().next_to(self.result))
            
            @property
            def allObjects(self):
                return [self.grid, *self.ridingLabels, *self.partyLabels,
                        *self.shareGrid, self.shareLabel, self.partyTitle,
                        self.partyTitleUnderline, self.winnerGrid, self.winnerLabel,
                        self.result, self.resultLabel, self.ridingLabel, *self.winners,
                        *self.votes, *self.winners, *self.voteShareObjects]
                      
            def updateRidingWinner(self, ridingId):
                return (self.partyLabels[self.ridingWinners[ridingId]].copy().move_to(self.winnerGrid[ridingId].get_center())
                        if self.ridingWinners[ridingId] != self.partyCount 
                        else Text("Tie").copy().move_to(self.winnerGrid[ridingId].get_center()))


            def partyVoteShares(self, partyId):
                    votesCast = sum([len(partySupporters.submobjects) for partySupporters in self.votes])          
                    firstRidingId = partyId * self.ridingCount 
                    votesforParty = self.votes[firstRidingId: firstRidingId + self.ridingCount]
                    votesRecieved = sum([len(partySupporters.submobjects) for partySupporters in votesforParty])
                    return (votesRecieved/votesCast)*100
            
            def updateOverallWinner(self):
                return (VGroup(*([self.partyLabels[party].copy() for party in self.largestParty]+[self.resultType]))
                                    .arrange_in_grid(rows=1).next_to(self.resultLabel, RIGHT))
            


        voteArray = [10,10,10,10,10,10,10,
                     11,11,11,11,11,11,11,
                     9, 9, 9, 9, 9, 9, 9,]
        map = ElectoralMap(voteArray)

        self.add(*map.allObjects)
        
        for obj in self.mobjects:
            obj.shift(UP * 0.4)
        self.remove(*map.allObjects)
        msg1 = VGroup(*[Text("Using First Past The Post,"),
                        Text("The same number of votes can lead to different outcomes,"),
                        Text("depending on how those votes are distributed across ridings.")]).arrange_in_grid(3).scale(0.75)
        #self.play(FadeIn(msg1))
        #self.wait()
        #self.play(FadeOut(msg1))
        self.play(FadeIn(*map.allObjects))

        self.wait(1)
        #self.play(*many_to_many(map, sourceIdList=[0,1,2],targetIdList=[3,4,5,6],n_votes=1))
        self.play(*one_to_many(map, sourceId=0, targetIdList=[3,4,5,6],n_votes=1),)
        self.play(*one_to_many(map, sourceId=1, targetIdList=[3,4,5,6],n_votes=1),)
        #self.play(*one_to_many(map, sourceId=2, targetIdList=[3,4,5,6],n_votes=1))
        self.wait(1)
        self.play(*one_to_many(map, sourceId=15, targetIdList=[16,17],n_votes=3),)
        self.play(*one_to_many(map, sourceId=18, targetIdList=[16,17],n_votes=3),)
        self.wait(1)
        self.play(*one_to_many(map, sourceId=9, targetIdList=[11], n_votes=4))
        self.play(*one_to_many(map, sourceId=10, targetIdList=[12], n_votes=4))
        #self.play(*one_to_many(map, sourceIdList=10, targetIdList=[11], n_votes=2))
        self.wait(1)
        self.play(*one_to_many(map, sourceId=11, targetIdList=[10], n_votes=4),
                  *one_to_many(map, sourceId=8, targetIdList=[9], n_votes=6),
                  *one_to_many(map, sourceId=16, targetIdList=[20], n_votes=4),
                  *one_to_many(map, sourceId=16, targetIdList=[14], n_votes=3))
        self.wait()
        self.play(*one_to_many(map, sourceId=16, targetIdList=[15], n_votes=4))
        self.wait(1)
        cut_to_text(1,["Consequently, a party can win the election",
                        "without receiving the most votes,",
                        "or win a majority while recieving",
                        "fewer than half the votes."])
        """
        anims+= 
        anims+= move_votes(self,sourceId=15,targetId=1,n_votes=1)
        anims+= move_votes(self,sourceId=2,targetId=9,n_votes=1)
        anims+= move_votes(self,sourceId=3,targetId=10,n_votes=1)
        anims+= move_votes(self,sourceId=4,targetId=11,n_votes=1)
        anims+= move_votes(self,sourceId=12,targetId=5,n_votes=1)
        anims+= move_votes(self,sourceId=13,targetId=20,n_votes=1)
        """

        #self.play(*map.swap_votes(sourceCol=0,targetCol=0,sourceRow=0,targetRow=2,n_votes=1))



        self.wait(1)
