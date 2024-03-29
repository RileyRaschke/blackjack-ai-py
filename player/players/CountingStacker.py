import json
from game.color import color
from game.score import score

import game.card as Card

from pprint import pprint

class Agent:
    def __init__(self, opts):
        self.disableAutoPlay = False
        self.newShoeFlag = False
        self.name = "CountingStacker"
        self.splitEnabled = True
        self.defaultBet = 10
        self.lastBet = self.defaultBet
        self.stackFactor = 2
        self.riskLevel = 1
        self.maxRisk = 20
        self.currHandCount = 0
        self.currCardCount = 0
        self.lastHandCount = 0
        self.shoeCount = 0
        self.cardCount = 0
        self.gameDecks = 6

    def _countRound(self, gameState):
        self.currHandCount = 0
        self.currCardCount = 0
        for seat in gameState:
            for player, hand in seat.items():
                for card in hand['hand']:
                    self.currCardCount += 1
                    if Card.value(card) in [10,11]:
                        self.currHandCount -= 1
                    elif Card.value(card) not in [7,8,9]:
                        self.currHandCount += 1

    def notifyNewShoe(self):
        self.newShoeFlag = True

    def _trueCount(self):
        decksRemaining = int(self.gameDecks-(self._cardCount()/52))
        if decksRemaining < 1:
            decksRemaining = 1
        return int(self._getCount()/decksRemaining)

    def _getCount(self):
        return self.shoeCount + self.currHandCount

    def _cardCount(self):
        return self.cardCount + self.currCardCount

    def placeBet(self, gameStateJson):
        #print( gameStateJson )
        if gameStateJson is None or gameStateJson == '':
            return self.lastBet

        gameState = json.loads(gameStateJson)
        dealer = gameState[-1]['dealer']
        myHands = self._myHands(gameState)

        if not self.newShoeFlag:
            self._countRound(gameState)
            self.lastHandCount = self.currHandCount
            self.shoeCount += self.currHandCount
            self.cardCount += self.currCardCount
            self.currHandCount = 0
            self.currCardCount = 0
            self.riskLevel = int(self.lastBet/self.defaultBet)
        else:
            print("Reset count for new shoe!")
            self.newShoeFlag = False
            self.currCardCount = 0
            self.currHandCount = 0
            self.lastHandCount = 0
            self.shoeCount = 0
            self.cardCount = 0
            self.riskLevel = 1
            self.lastBet = self.defaultBet

        lossFound = False
        for mySeat in myHands:
            if mySeat['score'] not in [score.blackjack, score.win]:
                lossFound = True

        if not lossFound and self.lastBet <= 40 and self._trueCount() > 5:
            self.lastBet = self.lastBet*self.stackFactor*2
            self.riskLevel += 2
            print( "%s:stacked bet! (%s)" % (self.name, self.lastBet))
        elif not lossFound and self.lastBet <= 40 and self._trueCount() > 1:
            self.lastBet = self.lastBet*self.stackFactor
            self.riskLevel += 1
            print( "%s:stacked bet! (%s)" % (self.name, self.lastBet))
        elif not lossFound and self.lastBet <= 40 and self._trueCount() >= 0:
            pass
        else:
            self.riskLevel = 1
            self.lastBet = self.defaultBet

        print("%s - Bet(%s) - True Count: %s" % (self.name, self.lastBet, self._trueCount()))
        return self.lastBet

    def _myHands(self, gameState):
        hands = []
        for seat in gameState:
            for player,res in seat.items():
                if player == 'player.players.CountingStacker2':
                    hands.append( res )
        return hands

    def _nextAction(self, gameStateJson, myHand):
        gameState = json.loads(gameStateJson)
        dealer = gameState[-1]['dealer']
        self._countRound(gameState)
        print("%s - NextAction - Shoe Count: %s" % (self.name, self._getCount()))
        if( self.riskLevel < self.maxRisk and self.splitEnabled and
            myHand.canSplit() and myHand.cards[0] not in [2,3,4,5,6] and
            (
                myHand.value() < 18
             or
                (myHand.value() in [18,20] and (dealer['handVal'] in [2,3,4,5,6] or dealer['handVal'] == 11) and self._getCount() > 6 )
             or
                (myHand.value() in [18,20] and (dealer['handVal'] in [2,3,4] and dealer['handVal'] != 11) and self._getCount() > 5 )
            )
        ):
            print("%s: action: SPLIT" % self.name)
            self.riskLevel *= 2
            return 'SPLIT'

        if(
            (myHand.value() in [10,11] and myHand.canDouble() and self._getCount() > 6)
            or
            (self.riskLevel < self.maxRisk and myHand.value() in [10,11] and myHand.canDouble() and dealer['handVal'] < 7 and self._getCount() > 2)
          ):
            print("%s: action: DOUBLE" % self.name)
            self.riskLevel *= 2
            return 'DOUBLE'

        if( myHand.value() >=17
         or (myHand.value() > 11 and not myHand.isSoft() and (dealer['handVal'] < 7 or self._getCount() > -2))
         or len(myHand.cards) > 5
        ):
            return 'STAND'
        else:
            return 'HIT'

    def nextAction(self, gameStateJson, myHand):
        action = self._nextAction( gameStateJson, myHand)
        print("%s - action: %s - True Count: %s" % (self.name, action, self._trueCount()))
        return action

    def init(self, gameState):
        print("Hello! I'm %s!" % self.name)
        pass

